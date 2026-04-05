import random
from snake import UP, DOWN, LEFT, RIGHT
from settings import COLS, ROWS

OPPOSITES = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}


class SnakeAI:
    """Open-space-seeking AI (v2).

    Every tick it scores all three non-reverse directions by how many free
    cells are reachable one step ahead of the destination (i.e. neighbor count
    of the destination cell).  A small straight-ahead bonus and random noise
    prevent jitter and make behaviour unpredictable.

    See snake-ai.md for the full feature log.
    """

    def decide(self, snake, all_occupied):
        """Return a direction for *snake* to queue this tick.

        Parameters
        ----------
        snake        : Snake instance
        all_occupied : set of (x, y) cells occupied by ALL snakes (alive + dead)
        """
        direction = snake.next_dir
        opposite  = OPPOSITES[direction]
        hx, hy    = snake.head()

        def step(d):
            return (hx + d[0], hy + d[1])

        def in_bounds(pos):
            x, y = pos
            return 0 <= x < COLS and 0 <= y < ROWS

        def is_safe(d):
            pos = step(d)
            return in_bounds(pos) and pos not in all_occupied

        def open_neighbors(d):
            """Count in-bounds, unoccupied cells adjacent to step(d)."""
            x, y = step(d)
            count = 0
            for nd in (UP, DOWN, LEFT, RIGHT):
                nx, ny = x + nd[0], y + nd[1]
                if 0 <= nx < COLS and 0 <= ny < ROWS and (nx, ny) not in all_occupied:
                    count += 1
            return count

        candidates = [d for d in (UP, DOWN, LEFT, RIGHT)
                      if d != opposite and is_safe(d)]

        if not candidates:
            # Completely boxed in — keep course and die on the wall
            return direction

        def score(d):
            straight_bonus = 0.3 if d == direction else 0.0
            return open_neighbors(d) + straight_bonus + random.uniform(0.0, 0.4)

        return max(candidates, key=score)
