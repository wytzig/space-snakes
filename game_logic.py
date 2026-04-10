"""
Authoritative server-side game logic.
No pygame dependency — pure Python only.
"""
import random
from settings import COLS, ROWS, UP, DOWN, LEFT, RIGHT, OPPOSITES, DIR_MAP

MAX_PLAYERS = 3
_SPAWN_XS = [COLS // 4, COLS // 2, 3 * COLS // 4]
SPAWN_POSITIONS = [(_SPAWN_XS[i], ROWS // 2) for i in range(MAX_PLAYERS)]

_ALL_CELLS = frozenset((x, y) for x in range(COLS) for y in range(ROWS))


class SnakeLogic:
    def __init__(self, player_id, sx, sy):
        self.player_id = player_id
        self.body = [(sx, sy), (sx - 1, sy), (sx - 2, sy)]
        self.direction = RIGHT
        self.next_dir = RIGHT
        self.grow_pending = 0
        self.score = 0
        self.alive = True

    def set_direction(self, dir_str):
        new_dir = DIR_MAP.get(dir_str)
        if new_dir and new_dir != OPPOSITES.get(self.direction):
            self.next_dir = new_dir

    def move(self, other_bodies):
        self.direction = self.next_dir
        hx, hy = self.body[0]
        dx, dy = self.direction
        new_head = (hx + dx, hy + dy)

        if not (0 <= new_head[0] < COLS and 0 <= new_head[1] < ROWS):
            self.alive = False
            return
        if new_head in self.body or new_head in other_bodies:
            self.alive = False
            return

        self.body.insert(0, new_head)
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            self.body.pop()

    def grow(self, amount=1):
        self.grow_pending += amount

    def head(self):
        return self.body[0]

    def respawn(self, empty_cells):
        candidates = [
            (sx, sy) for sx, sy in SPAWN_POSITIONS
            if all((sx - i, sy) in empty_cells for i in range(3))
        ]
        if not candidates:
            for y in range(2, ROWS - 2):
                for x in range(2, COLS - 3):
                    if all((x - i, y) in empty_cells for i in range(3)):
                        candidates.append((x, y))
                        break
                if candidates:
                    break
        if not candidates:
            return  # grid is so full we cannot respawn; try again next tick
        sx, sy = random.choice(candidates)
        self.body = [(sx, sy), (sx - 1, sy), (sx - 2, sy)]
        self.direction = RIGHT
        self.next_dir = RIGHT
        self.grow_pending = 0
        self.alive = True


class GameSession:
    def __init__(self):
        self.snakes = {}   # player_id -> SnakeLogic
        self.foods = set()
        self._spawn_food()

    # --- internal helpers ---

    def _alive_bodies(self, exclude_id=None):
        occ = set()
        for pid, s in self.snakes.items():
            if pid != exclude_id and s.alive:
                occ.update(s.body)
        return occ

    def _empty_cells(self):
        occ = self._alive_bodies()
        occ.update(self.foods)
        return _ALL_CELLS - occ

    def _spawn_food(self):
        empty = self._empty_cells()
        if empty:
            self.foods.add(random.choice(list(empty)))

    # --- public API ---

    def add_player(self):
        """Assign the lowest free slot (0–2) as player_id. Returns id or None if full."""
        for slot in range(MAX_PLAYERS):
            if slot not in self.snakes:
                sx, sy = SPAWN_POSITIONS[slot]
                self.snakes[slot] = SnakeLogic(slot, sx, sy)
                return slot
        return None

    def remove_player(self, player_id):
        self.snakes.pop(player_id, None)

    def reset(self):
        self.snakes.clear()
        self.foods.clear()
        self._spawn_food()

    def tick(self):
        if not self.snakes:
            return

        was_alive = {pid: s.alive for pid, s in self.snakes.items()}

        # Move all currently-alive snakes
        for pid, snake in self.snakes.items():
            if not snake.alive:
                continue
            other_bodies = self._alive_bodies(exclude_id=pid)
            snake.move(other_bodies)

        # Head-on collision: two snakes whose heads landed on the same cell
        head_map = {}
        for pid, snake in self.snakes.items():
            if snake.alive:
                h = snake.head()
                if h in head_map:
                    snake.alive = False
                    self.snakes[head_map[h]].alive = False
                else:
                    head_map[h] = pid

        # Newly dead snakes: body -> food, then immediate respawn
        newly_dead = [pid for pid, s in self.snakes.items() if was_alive[pid] and not s.alive]

        for pid in newly_dead:
            for cell in self.snakes[pid].body:
                self.foods.add(cell)

        for pid in newly_dead:
            snake = self.snakes[pid]
            other_occ = self._alive_bodies()   # alive snakes post-move
            other_occ.update(self.foods)
            empty = _ALL_CELLS - other_occ
            snake.respawn(empty)

        # Food eating (checked after respawn so fresh spawns don't eat)
        for snake in self.snakes.values():
            if snake.alive:
                h = snake.head()
                if h in self.foods:
                    self.foods.discard(h)
                    snake.grow()
                    snake.score += 10

        if not self.foods:
            self._spawn_food()

    def get_state(self):
        return {
            "snakes": [
                {"id": pid, "body": list(s.body), "score": s.score, "alive": s.alive}
                for pid, s in self.snakes.items()
            ],
            "foods": list(self.foods),
        }
