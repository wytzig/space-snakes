"""
Authoritative WebSocket game server.
Run with: python3 server.py

Requires: python3 -m pip install websockets
Deploy to Render / Railway for GitHub Pages multiplayer.
"""
import asyncio
import json
import websockets
from settings import SPEED_NORMAL, FPS
from game_logic import GameSession

TICK_INTERVAL = SPEED_NORMAL / FPS   # seconds between game ticks (~0.133 s)

session = GameSession()
connected = {}    # websocket -> player_id


async def _broadcast_state():
    if not connected:
        return
    base = session.get_state()
    for ws, pid in list(connected.items()):
        msg = json.dumps({"type": "state", "player_id": pid, **base})
        try:
            await ws.send(msg)
        except Exception:
            pass


async def _game_loop():
    while True:
        await asyncio.sleep(TICK_INTERVAL)
        if connected:
            session.tick()
            await _broadcast_state()


async def _handler(websocket):
    player_id = session.add_player()
    if player_id is None:
        await websocket.send(json.dumps({"type": "error", "msg": "game full"}))
        return

    connected[websocket] = player_id
    await websocket.send(json.dumps({"type": "joined", "player_id": player_id}))
    print(f"Player {player_id} connected  ({len(connected)} total)")

    try:
        async for raw in websocket:
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if data.get("type") == "input" and "dir" in data:
                snake = session.snakes.get(player_id)
                if snake:
                    snake.set_direction(data["dir"])
    except Exception:
        pass
    finally:
        connected.pop(websocket, None)
        session.remove_player(player_id)
        print(f"Player {player_id} disconnected  ({len(connected)} total)")
        if not connected:
            session.reset()
            print("Lobby empty — session reset")


async def main():
    loop = asyncio.get_running_loop()
    loop.create_task(_game_loop())
    async with websockets.serve(_handler, "0.0.0.0", 8765):
        print("Space Snakes server running on ws://0.0.0.0:8765")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
