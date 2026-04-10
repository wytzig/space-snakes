"""
Thin async wrapper around the WebSocket connection.

Two paths:
  - sys.platform == "emscripten" (Pygbag/WASM): creates the WebSocket via
    js.eval() and keeps ALL callbacks in pure JavaScript. Python only polls
    JS globals — no Python-to-JS callback crossing, no create_proxy needed.
  - Otherwise (local desktop): uses the websockets package over TCP.

Requires (desktop only): python3 -m pip install websockets
"""
import sys
import asyncio
import json


class ClientNet:
    def __init__(self, url):
        self.url = url
        self.player_id = None
        self.latest_state = None
        self._ws = None
        self._connected = False
        self._send_queue = None   # desktop only
        self.connect_status = ""  # human-readable progress shown in the UI

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    async def connect(self):
        if sys.platform == "emscripten":
            await self._connect_browser()
        else:
            await self._connect_desktop()

    def poll(self):
        """Drain buffered messages. Must be called every frame on emscripten."""
        if sys.platform != "emscripten" or not self._connected:
            return
        import js  # noqa: PLC0415
        # Read and clear the JS message buffer in one splice call
        msgs = js.eval("window._ss_msgs.splice(0)")
        for i in range(msgs.length):
            self._process_message(str(msgs[i]))
        # Detect dropped connection
        if js.eval("window._ss_closed"):
            self._connected = False

    def send_direction(self, direction):
        if sys.platform == "emscripten":
            if self._connected:
                import js  # noqa: PLC0415
                # Two json.dumps calls are intentional, not a bug:
                #   inner call  → produces the JSON string the server expects, e.g. '{"type":"input","dir":"UP"}'
                #   outer call  → encodes that string as a JS string literal (adds surrounding quotes + escaping)
                #                 so it can be safely spliced into js.eval() as `ws.send(<literal>)`.
                payload = json.dumps(json.dumps({"type": "input", "dir": direction}))
                js.eval(f"window._ss_ws && window._ss_ws.send({payload})")
        else:
            if self._send_queue is not None:
                self._send_queue.put_nowait({"type": "input", "dir": direction})

    def get_state(self):
        return self.latest_state

    def is_connected(self):
        return self._connected

    async def close(self):
        self._connected = False
        if sys.platform == "emscripten":
            try:
                import js  # noqa: PLC0415
                js.eval("window._ss_ws && window._ss_ws.close()")
            except Exception:
                pass
        elif self._ws:
            await self._ws.close()

    # ------------------------------------------------------------------ #
    # Browser path — all WS callbacks stay in pure JavaScript             #
    # ------------------------------------------------------------------ #

    async def _connect_browser(self):
        import js  # noqa: PLC0415

        # Inject a self-contained JS WebSocket with a plain-array message
        # buffer.  No Python functions are assigned as JS callbacks, so
        # create_proxy / GC issues cannot occur.
        MAX_ATTEMPTS = 3
        TIMEOUT_S = 15.0   # per attempt; covers Render free-tier cold start (~30s total)

        for attempt in range(1, MAX_ATTEMPTS + 1):
            self.connect_status = f"Connecting... (attempt {attempt}/{MAX_ATTEMPTS})"
            js.eval(f"""
            window._ss_open   = false;
            window._ss_closed = false;
            window._ss_msgs   = [];
            (function() {{
                var ws = new WebSocket({json.dumps(self.url)});
                window._ss_ws = ws;
                ws.onopen    = function()  {{ window._ss_open = true; }};
                ws.onclose   = function()  {{ window._ss_open = false;
                                             window._ss_closed = true; }};
                ws.onmessage = function(e) {{ window._ss_msgs.push(e.data); }};
            }})();
            """)

            waited = 0.0
            while (not js.eval("window._ss_open")
                   and not js.eval("window._ss_closed")
                   and waited < TIMEOUT_S):
                await asyncio.sleep(0.1)
                waited += 0.1

            if js.eval("window._ss_open"):
                self._connected = True
                self.connect_status = ""
                return

            print(f"[connect] attempt {attempt}/{MAX_ATTEMPTS} failed (closed after {waited:.1f}s)")
            if attempt < MAX_ATTEMPTS:
                self.connect_status = f"Retrying... ({attempt}/{MAX_ATTEMPTS} failed)"
                await asyncio.sleep(5.0)

        self.connect_status = ""
        raise ConnectionError(
            f"Could not connect after {MAX_ATTEMPTS} attempts. "
            "The server may still be waking up — try again in 30 seconds."
        )

    # ------------------------------------------------------------------ #
    # Desktop path (websockets package)                                   #
    # ------------------------------------------------------------------ #

    async def _connect_desktop(self):
        try:
            import websockets as _ws_pkg  # noqa: PLC0415
        except ImportError as exc:
            raise RuntimeError(
                "websockets not installed — run: python3 -m pip install websockets"
            ) from exc

        self._send_queue = asyncio.Queue()
        self._ws = await _ws_pkg.connect(self.url)
        self._connected = True
        loop = asyncio.get_running_loop()
        loop.create_task(self._recv_loop())
        loop.create_task(self._send_loop())

    async def _recv_loop(self):
        try:
            async for raw in self._ws:
                self._process_message(raw)
        except Exception as exc:
            print(f"[recv_loop] disconnected: {exc}")
            self._connected = False

    async def _send_loop(self):
        while self._connected:
            try:
                msg = await asyncio.wait_for(self._send_queue.get(), timeout=1.0)
                await self._ws.send(json.dumps(msg))
            except asyncio.TimeoutError:
                continue
            except Exception as exc:
                print(f"[send_loop] disconnected: {exc}")
                self._connected = False
                break

    # ------------------------------------------------------------------ #
    # Shared message handling                                              #
    # ------------------------------------------------------------------ #

    def _process_message(self, raw):
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return
        t = data.get("type")
        if t == "joined":
            self.player_id = data["player_id"]
        elif t == "state":
            self.latest_state = data
        elif t == "error":
            print(f"[server] {data.get('msg')}")
            self._connected = False
