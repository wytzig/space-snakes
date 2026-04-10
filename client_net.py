"""
Thin async wrapper around the WebSocket connection.

Two paths:
  - sys.platform == "emscripten" (Pygbag/WASM): uses js.WebSocket via the
    browser's native API. The websockets package does not work here.
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
        # Desktop-only send queue
        self._send_queue = None
        # Browser-only pending message buffer (filled by JS callbacks)
        self._pending_msgs = []

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    async def connect(self):
        if sys.platform == "emscripten":
            await self._connect_browser()
        else:
            await self._connect_desktop()

    def poll(self):
        """
        Process buffered messages from the JS WebSocket callback.
        Must be called every frame on emscripten; no-op on desktop.
        """
        if sys.platform == "emscripten" and self._pending_msgs:
            for raw in self._pending_msgs:
                self._process_message(raw)
            self._pending_msgs.clear()

    def send_direction(self, direction):
        """Non-blocking: queue or send a direction input string."""
        if sys.platform == "emscripten":
            if self._ws and self._connected:
                self._ws.send(json.dumps({"type": "input", "dir": direction}))
        else:
            if self._send_queue is not None:
                self._send_queue.put_nowait({"type": "input", "dir": direction})

    def get_state(self):
        return self.latest_state

    def is_connected(self):
        return self._connected

    async def close(self):
        self._connected = False
        if self._ws:
            if sys.platform == "emscripten":
                self._ws.close()
                # Release Pyodide proxies so JS-held references don't leak
                for attr in ("_proxy_on_message", "_proxy_on_close"):
                    proxy = getattr(self, attr, None)
                    if proxy is not None:
                        proxy.destroy()
            else:
                await self._ws.close()

    # ------------------------------------------------------------------ #
    # Browser path (js.WebSocket)                                         #
    # ------------------------------------------------------------------ #

    async def _connect_browser(self):
        import js  # only available inside Pygbag/emscripten  # noqa: PLC0415
        from pyodide.ffi import create_proxy  # noqa: PLC0415

        # js.eval is more compatible than js.WebSocket.new() across Pyodide
        # versions — the .new attribute is None in some Pygbag builds.
        ws = js.eval(f"new WebSocket({json.dumps(self.url)})")
        self._ws = ws

        # create_proxy keeps the closures alive across GC cycles while JS
        # still holds a reference to them.
        self._proxy_on_message = create_proxy(lambda e: self._pending_msgs.append(e.data))
        self._proxy_on_close = create_proxy(lambda e: setattr(self, "_connected", False))

        ws.onmessage = self._proxy_on_message
        ws.onclose = self._proxy_on_close

        # Poll readyState until OPEN (1) or CLOSED (3)
        while ws.readyState == 0:   # CONNECTING
            await asyncio.sleep(0.05)

        if ws.readyState != 1:      # not OPEN
            raise ConnectionError(f"WebSocket failed (readyState={ws.readyState})")

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
