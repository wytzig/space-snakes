# Space Snakes

> 16-bit retro multiplayer snake with neon laser visuals, set in the cosmos.

![alt text](image.png)
![alt text](image-1.png)

Up to 3 players connect from any browser. When a snake dies its body turns into food and it respawns immediately — no waiting.

---

## Features

- [x] Online multiplayer — up to 3 players
- [x] Neon laser snake with glow effect (green / cyan / pink per player)
- [x] Scrolling starfield background
- [x] Retro pixel font UI
- [x] WASD / arrow key controls
- [x] Death-to-food respawn mechanic
- [x] Background music (space_snakes.mpeg loops; M key or button to mute)
- [ ] Sound effects (eat, death, boost)
- [ ] Background themes (nebula, asteroid field)
- [ ] Power-ups (speed boost, shield)
- [ ] High score persistence
- [ ] Particle effects

---

## Play Online

The game runs in your browser via GitHub Pages. Multiplayer needs two things:

| Part | What it is | Where it runs |
|---|---|---|
| **Game client** | The playable game (compiled to WASM by Pygbag) | GitHub Pages (free, static) |
| **Game server** | Keeps all players in sync over WebSocket | Render.com (free web service) |

**Step 1 — Deploy the server to Render** (one-time, ~5 minutes)

1. Create a free account at [render.com](https://render.com)
2. Click **"New +"** → **"Web Service"**
3. Choose **"Build and deploy from a Git repository"**
4. Connect your GitHub account and select the **space-snakes** repo
5. Render will detect `render.yaml` automatically and fill in the settings
6. Click **"Create Web Service"**
7. Wait ~2 minutes for the build to finish
8. Copy the URL shown at the top — it looks like:
   ```
   https://space-snakes-server.onrender.com
   ```
   That is your server URL.

> **Note:** The free Render plan spins down after 15 minutes of inactivity. The first player to connect may wait ~30 seconds for it to wake up. After that it is fast.

---

**Step 2 — Enable GitHub Pages**

1. Go to your repo on GitHub → **Settings** → **Pages** (left sidebar)
2. Under **"Build and deployment"**, change **Source** to **"GitHub Actions"**
3. Go to the **Actions** tab and click **"Deploy to GitHub Pages"**
4. Click **"Run workflow"** → **"Run workflow"** (green button)
5. Wait ~2 minutes for the build and deploy to finish
6. Your game is now live at:
   ```
   https://wytzig.github.io/space-snakes/
   ```

---

**Step 3 — Share the link with friends**

Open the game URL with your server address added as a `?ws=` parameter:

```
https://wytzig.github.io/space-snakes/?ws=wss://YOUR-SERVER.onrender.com
```

Example:
```
https://wytzig.github.io/space-snakes/?ws=wss://space-snakes-server.onrender.com
```

Send this exact link to up to 2 friends. Each person opens it in their browser, presses **Enter**, and joins the game. No login needed.

> The `wss://` prefix (not `ws://`) is required — browsers block unencrypted connections from HTTPS pages.

---

## Controls

| Key | Action |
|---|---|
| Arrow keys / WASD | Steer your snake |
| F | Toggle fullscreen |
| M | Toggle music mute |
| ESC | Back to menu |

---

## Run Locally (Python)

To play on your own machine (no browser needed):

**Terminal 1 — start the server:**

```bash
python3 -m pip install websockets
python3 server.py
```

**Terminal 2 — start the game client:**

```bash
sudo apt install python3-pygame   # WSL/Ubuntu: avoids SDL build errors
python3 main.py
```

Open a third terminal (or ask a friend on the same network) and run `python3 main.py` again to add a second player.

---

## WSL / Linux Display Note

If running under WSL without WSLg, you need an X server (VcXsrv, Xming, or WSLg) and:

```bash
export DISPLAY=:0
python3 main.py
```

---

## Architecture

```
Browser (GitHub Pages)          Render.com (free)
+----------------------------+  +----------------------+
| index.html                 |  |                      |
| game.wasm  (Pygbag/Python) |<-| server.py            |
| assets/                    |  | (asyncio WebSocket)  |
+----------------------------+  +----------------------+
         WebSocket (wss://)
```

- `server.py` — authoritative game loop; all collision and food logic lives here
- `client_net.py` — thin WebSocket wrapper; uses `js.WebSocket` in WASM, `websockets` package locally
- `game_logic.py` — pure Python game rules (no pygame), shared with the server
- `game.py` — renders the state received from the server
- `main.py` — async entry point (compatible with both Python and Pygbag WASM)
