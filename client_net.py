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
                # json.dumps encodes the payload string as a JS string literal
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

        # Poll until the socket opens or definitively fails
        while not js.eval("window._ss_open") and not js.eval("window._ss_closed"):
            await asyncio.sleep(0.05)

        if not js.eval("window._ss_open"):
            raise ConnectionError(
                "WebSocket could not connect — is the server running and reachable?"
            )

        self._connected = True

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
        except Exception:
            self._connected = False

    async def _send_loop(self):
        while self._connected:
            try:
                msg = await asyncio.wait_for(self._send_queue.get(), timeout=1.0)
                await self._ws.send(json.dumps(msg))
            except asyncio.TimeoutError:
                continue
            except Exception:
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
