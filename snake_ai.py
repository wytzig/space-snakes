import random
from collections import deque
from snake import UP, DOWN, LEFT, RIGHT
from settings import COLS, ROWS

OPPOSITES = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}


def _bfs_nearest(start, goals, blocked):
    """BFS from start; return (first_step_direction, distance) to the nearest cell in goals.
    Returns (None, inf) if no goal is reachable."""
    if not goals:
        return None, float('inf')
    if start in goals:
        return None, 0
    visited = {start}
    queue = deque([(start, None, 0)])  # (pos, first-step dir, distance)
    while queue:
        pos, first_dir, dist = queue.popleft()
        for d in (UP, DOWN, LEFT, RIGHT):
            npos = (pos[0] + d[0], pos[1] + d[1])
            if npos in visited or npos in blocked:
                continue
            if not (0 <= npos[0] < COLS and 0 <= npos[1] < ROWS):
                continue
            fd = first_dir if first_dir is not None else d
            if npos in goals:
                return fd, dist + 1
            visited.add(npos)
            queue.append((npos, fd, dist + 1))
    return None, float('inf')


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

    def decide(self, snake, all_occupied, food_pos, corpse_pellets=None):
        direction  = snake.next_dir
        opposite   = OPPOSITES[direction]
        hx, hy     = snake.head()
        body_len   = len(snake.body)
        greediness = snake.greediness  # 0.0 = very cautious, 1.0 = reckless

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

        # Personality: greedy snakes accept tighter spaces when chasing food.
        # greediness=0.0 needs full body_len free cells (very safe).
        # greediness=1.0 only needs ~25% of body_len free cells (reckless).
        threshold = max(2, int(body_len * (1.0 - greediness * 0.75)))

        # Find nearest target: main food pellet OR any corpse pellet, whichever is closer
        food_dir, food_dist = _bfs_nearest((hx, hy), {food_pos}, all_occupied)
        corpse_goals = set(corpse_pellets.keys()) if corpse_pellets else set()
        corpse_dir, corpse_dist = _bfs_nearest((hx, hy), corpse_goals, all_occupied)

        # Pick the closer reachable target; prefer main food on a tie (worth more)
        if corpse_dist < food_dist:
            target_dir = corpse_dir
        else:
            target_dir = food_dir

        if target_dir in candidates and space[target_dir] >= threshold:
            return target_dir

        # Safety fallback: go where there is the most room.
        # Greedy snakes add more noise — they pick erratically rather than always
        # taking the mathematically safest path.
        noise_scale = 0.5 + greediness * 1.5
        return max(candidates, key=lambda d: space[d] + random.uniform(0, noise_scale))
