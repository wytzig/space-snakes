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
                for attr in ("_proxy_on_message", "_proxy_on_close"):
                    proxy = getattr(self, attr, None)
                    if proxy is not None:
                        try:
                            proxy.destroy()
                        except Exception:
                            pass
            else:
                await self._ws.close()

    # ------------------------------------------------------------------ #
    # Browser path (js.WebSocket)                                         #
    # ------------------------------------------------------------------ #

    async def _connect_browser(self):
        # Pygbag/Pyodide builds vary — try every known working approach in order.
        import js  # noqa: PLC0415

        ws = self._make_browser_ws(js, self.url)
        self._ws = ws
        self._attach_browser_callbacks(js, ws)

        while ws.readyState == 0:       # CONNECTING
            await asyncio.sleep(0.05)

        if ws.readyState != 1:          # not OPEN
            raise ConnectionError(f"WebSocket failed (readyState={ws.readyState})")

        self._connected = True

    @staticmethod
    def _make_browser_ws(js, url):
        """Try every known way to construct a browser WebSocket."""
        attempts = [
            lambda: js.window.WebSocket.new(url),
            lambda: js.WebSocket.new(url),
            lambda: js.eval(f"new WebSocket({json.dumps(url)})"),
            lambda: getattr(js, "globalThis").WebSocket.new(url),
        ]
        last_err = None
        for attempt in attempts:
            try:
                ws = attempt()
                if ws is not None:
                    return ws
            except Exception as exc:
                last_err = exc
        raise ConnectionError(f"Cannot create WebSocket in this browser: {last_err}")

    def _attach_browser_callbacks(self, js, ws):
        """Attach onmessage / onclose, with and without create_proxy."""
        def _on_msg(e):
            self._pending_msgs.append(e.data)

        def _on_close(e):
            self._connected = False

        try:
            from pyodide.ffi import create_proxy  # noqa: PLC0415
            self._proxy_on_message = create_proxy(_on_msg)
            self._proxy_on_close   = create_proxy(_on_close)
            ws.onmessage = self._proxy_on_message
            ws.onclose   = self._proxy_on_close
        except Exception:
            # Older Pyodide: direct assignment works without create_proxy
            self._cb_message = _on_msg
            self._cb_close   = _on_close
            ws.onmessage = _on_msg
            ws.onclose   = _on_close

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
