# Feature: Local server fix + itch.io publishing

## Issue 1 — "Could not connect: Connect call failed ('127.0.0.1', 8765)"

This is NOT a code bug. It means `server.py` is not running.
The game client always tries to reach a WebSocket server; if nothing is listening on port 8765 you get Errno 111.

**Fix: run the server first** (Terminal 1):
```
python3 server.py
```
Then in Terminal 2:
```
python3 main.py
```

No code change needed. The README already documents this, so no doc update required either.

---

## Issue 2 — itch.io publishing

### Do you have WASM? Yes.
Pygbag already builds a self-contained HTML5 bundle in `build/web/` via the GitHub Actions workflow.
That output is exactly what itch.io expects for an HTML5 game upload.

### Existing relevant code
- `main.py:_start_music()` — called immediately after `pygame.init()`, before any user interaction.
- `settings.py:MUSIC_PATH` points to `assets/sounds/space_snakes.mpeg`.

### Problems to fix for browser/itch.io

**A. Autoplay policy (breaking):** Browsers block audio that starts before the first user gesture.
`_start_music()` is currently called at startup — it will silently fail in every browser/itch.io run.
Fix: track `_music_started` in `main.py`; call `_start_music()` once on the first `KEYDOWN` or `MOUSEBUTTONDOWN` event.

**B. Audio format:** `.mpeg` (MP3) has inconsistent support through Pygbag's WASM audio layer.
`.ogg` (Vorbis) is the most reliable cross-browser format for Pygame/Pygbag.
No code change — but document in README that users should convert the file if music doesn't play.
(Conversion not automated here because it requires ffmpeg, which is not a project dependency.)

**C. SharedArrayBuffer (itch.io-specific setting):** Pygbag WASM requires COOP/COEP security headers
to use SharedArrayBuffer. On itch.io, this is a per-game toggle in the game settings page
("This file uses SharedArrayBuffer"). Must be enabled or the game won't load at all.

### Code change (A only)
| File | Change |
|---|---|
| `main.py` | Add `_music_started = False`; on first user input event, call `_start_music()` and set flag |

### Doc changes
| File | Change |
|---|---|
| `docs/README.md` | Add "Publish to itch.io" section covering build, zip, upload, SharedArrayBuffer toggle, WS URL |
