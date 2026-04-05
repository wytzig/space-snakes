import random
from collections import deque
from snake import UP, DOWN, LEFT, RIGHT
from settings import COLS, ROWS

OPPOSITES = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}


def _bfs_dir(start, goal, blocked):
    """BFS from start toward goal; return the direction of the first step, or None if unreachable."""
    if start == goal:
        return None
    visited = {start}
    queue = deque([(start, None)])  # (position, first-step direction)
    while queue:
        pos, first_dir = queue.popleft()
        for d in (UP, DOWN, LEFT, RIGHT):
            npos = (pos[0] + d[0], pos[1] + d[1])
            if npos in visited or npos in blocked:
                continue
            if not (0 <= npos[0] < COLS and 0 <= npos[1] < ROWS):
                continue
            fd = first_dir if first_dir is not None else d
            if npos == goal:
                return fd
            visited.add(npos)
            queue.append((npos, fd))
    return None  # food unreachable


def _flood_fill(start, blocked):
    """Count all grid cells reachable from start without crossing blocked cells."""
    if start in blocked:
        return 0
    visited = {start}
    queue = deque([start])
    while queue:
        pos = queue.popleft()
        for d in (UP, DOWN, LEFT, RIGHT):
            npos = (pos[0] + d[0], pos[1] + d[1])
            if (0 <= npos[0] < COLS and 0 <= npos[1] < ROWS
                    and npos not in blocked and npos not in visited):
                visited.add(npos)
                queue.append(npos)
    return len(visited)


class SnakeAI:
    """Food-seeking + flood-fill safety AI (v3).

    Each tick:
    1. BFS to find the shortest path to food and note its first step.
    2. Flood-fill each candidate direction to count reachable open area.
    3. If the food-path direction leads to enough room (>= snake body length),
       chase the food — snakes eagerly race toward pellets.
    4. If the food path is too tight (snake risks self-trapping), fall back to
       the direction with the most reachable space instead.

    This means short snakes are aggressive food hunters, while long snakes
    become cautious and pick routes that keep space to manoeuvre.

    See snake-ai.md for the full feature log.
    """

    def decide(self, snake, all_occupied, food_pos):
        direction = snake.next_dir
        opposite  = OPPOSITES[direction]
        hx, hy    = snake.head()
        body_len  = len(snake.body)

        def step(d):
            return (hx + d[0], hy + d[1])

        def is_safe(d):
            x, y = step(d)
            return 0 <= x < COLS and 0 <= y < ROWS and step(d) not in all_occupied

        candidates = [d for d in (UP, DOWN, LEFT, RIGHT)
                      if d != opposite and is_safe(d)]

        if not candidates:
            return direction  # completely trapped; will die on next step

        # Reachable area from each candidate — the key signal for self-trap avoidance
        space = {d: _flood_fill(step(d), all_occupied) for d in candidates}

        # Shortest path to food
        food_dir = _bfs_dir((hx, hy), food_pos, all_occupied)

        # Chase food only when the route stays open enough to survive
        if food_dir in candidates and space[food_dir] >= body_len:
            return food_dir

        # Safety fallback: go where there is the most room
        # Small noise breaks ties and keeps movement varied
        return max(candidates, key=lambda d: space[d] + random.uniform(0, 0.5))
