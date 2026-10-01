# agent.py
import random
from collections import deque
import heapq
import math


class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        pos = percept.get('agent_pos')
        return random.choice(self.actions_pool)


# ===== ADDED (Lab 02 - Step 1.2: Simple Reflex Agent) =====
class SimpleReflexAgent:
    """
    A Simple Reflex Agent

    Selects an action using ONLY the current percept - strictly IF-THEN
    Condition-Action rules. No __init__ memory, no history of any kind.
    This is exactly what makes it fail in a partially observable
    environment: it cannot tell that it has been in this exact situation
    before, so it will repeat the same mistake forever.
    """

    def sense_and_act(self, percept: dict) -> str:
        # --- Condition-Action Rules ---
        # IF food_here THEN suck (eat the food on the current cell)
        if percept.get('food_here'):
            return 'Suck'

        # IF wall_ahead THEN turn_left (attempt to move Left instead)
        if percept.get('wall_ahead'):
            return 'Left'

        # ELSE move_forward (default: keep moving Up)
        return 'Up'
# ===== END ADDED (Step 1.2) =====


# ===== ADDED (Lab 02 - Step 1.3: Model-Based Agent) =====
class ModelBasedAgent:
    """
    A Model-Based Reflex Agent (Lecture 03).

    Unlike SimpleReflexAgent, this agent maintains an internal memory state
    across calls, so it can recognize when it is repeating itself and break
    out of a loop that a Simple Reflex Agent would be stuck in forever.
    """

    def __init__(self):
        # --- Internal memory state ---
        self.percept_history = []          # every percept ever received
        self.action_history = []           # every action ever taken
        self.visited_cells = set()         # placeholder for spatial memory
        # Maps a percept "signature" -> the last action tried in response
        # to it. This is what lets the agent notice "I already tried Left
        # here and it didn't work, so this time I'll try something else."
        self.percept_action_memory = {}

    def _signature(self, percept: dict) -> tuple:
        """Turns a percept dict into a hashable signature so it can be used
        as a memory key."""
        return (percept.get('wall_ahead'), percept.get('food_here'))

    def sense_and_act(self, percept: dict) -> str:
        # --- Step 1: Update internal state (Transition Model + Sensor Model) ---
        # Transition Model: record what the world just showed us.
        self.percept_history.append(dict(percept))
        signature = self._signature(percept)

        # --- Step 2: Condition-Action rules that consult memory ---
        if percept.get('food_here'):
            action = 'Suck'

        elif percept.get('wall_ahead'):
            # Sensor Model: check what action we tried LAST TIME we were in
            # this exact situation (same percept signature).
            previous_response = self.percept_action_memory.get(signature)

            if previous_response == 'Left':
                # We already tried turning left from here and hit a wall
                # again -> memory tells us to try the opposite direction.
                action = 'Right'
            elif previous_response == 'Right':
                action = 'Down'
            else:
                # First time seeing this wall -> default reflex response.
                action = 'Left'
        else:
            action = 'Up'

        # Record what we just decided, keyed by the situation we saw,
        # so next time we recognize the repeat and can choose differently.
        self.percept_action_memory[signature] = action
        self.action_history.append(action)
        return action
# ===== END ADDED (Step 1.3) =====


class SearchAgent:
    """Find paths using BFS, DFS, UCS, or heuristic-guided A* search."""

    _MOVES = (
        ('Up', (0, 1)),
        ('Down', (0, -1)),
        ('Left', (-1, 0)),
        ('Right', (1, 0)),
    )

    def __init__(self):
        self.plan = []
        self.active_algo = 'AStar'
        self.heuristic_type = 'manhattan'
        self.last_expanded = 0
        # The environment starts every agent at (0, 0). Because the percept
        # does not expose agent_pos, track it as planned actions are executed.
        self.current_pos = (0, 0)

    def sense_and_act(self, percept: dict) -> str:
        """Create an offline plan when needed and execute one action from it."""
        # Remain compatible with environments that do expose the position.
        if percept.get('agent_pos') is not None:
            self.current_pos = tuple(percept['agent_pos'])

        if not self.plan:
            food_positions = [tuple(food) for food in percept['all_food']]
            if not food_positions:
                return 'Suck'

            # Manhattan distance identifies the closest pellet on the grid.
            goal = min(
                food_positions,
                key=lambda food: (
                    abs(food[0] - self.current_pos[0])
                    + abs(food[1] - self.current_pos[1])
                )
            )

            search_methods = {
                'BFS': self.bfs_search,
                'DFS': self.dfs_search,
                'UCS': self.ucs_search,
                'ASTAR': lambda *args: self.astar_search(
                    *args, heuristic_type=self.heuristic_type),
            }
            algorithm = self.active_algo.upper()
            if algorithm not in search_methods:
                raise ValueError(
                    "active_algo must be 'BFS', 'DFS', 'UCS', or 'AStar'"
                )

            self.plan = search_methods[algorithm](
                self.current_pos,
                goal,
                percept['walls'],
                percept['grid_size']
            ) or []

            # If the closest pellet is unreachable, try the remaining pellets
            # in distance order instead of failing with an empty-plan pop.
            if not self.plan and goal != self.current_pos:
                other_food = sorted(
                    (food for food in food_positions if food != goal),
                    key=lambda food: (
                        abs(food[0] - self.current_pos[0])
                        + abs(food[1] - self.current_pos[1])
                    )
                )
                for alternate_goal in other_food:
                    self.plan = search_methods[algorithm](
                        self.current_pos,
                        alternate_goal,
                        percept['walls'],
                        percept['grid_size']
                    ) or []
                    if self.plan:
                        break

        if not self.plan:
            return 'Suck'

        # Predict the next position so the following planning cycle starts
        # from the state reached by this action.
        action = self.plan[0]
        move = dict(self._MOVES)[action]
        self.current_pos = (
            self.current_pos[0] + move[0],
            self.current_pos[1] + move[1]
        )
        return self.plan.pop(0)

    def _successors(self, state, walls, grid_size):
        """Yield valid neighbouring states and the actions that reach them."""
        width, height = grid_size
        x, y = state

        for action, (dx, dy) in self._MOVES:
            next_state = (x + dx, y + dy)
            if (0 <= next_state[0] < width
                    and 0 <= next_state[1] < height
                    and next_state not in walls):
                yield next_state, action

    def bfs_search(self, start_pos, goal_pos, walls, grid_size):
        """Return a shortest action path using a FIFO frontier."""
        start = tuple(start_pos)
        goal = tuple(goal_pos)
        wall_set = set(map(tuple, walls))

        frontier = deque([(start, [])])
        reached = {start}
        self.last_expanded = 0

        while frontier:
            state, path = frontier.popleft()
            if state == goal:
                return path

            self.last_expanded += 1
            for next_state, action in self._successors(
                    state, wall_set, grid_size):
                if next_state not in reached:
                    reached.add(next_state)
                    frontier.append((next_state, path + [action]))

        return None

    def dfs_search(self, start_pos, goal_pos, walls, grid_size):
        """Return an action path using a LIFO frontier."""
        start = tuple(start_pos)
        goal = tuple(goal_pos)
        wall_set = set(map(tuple, walls))

        frontier = [(start, [])]
        reached = {start}

        while frontier:
            state, path = frontier.pop()
            if state == goal:
                return path

            for next_state, action in self._successors(
                    state, wall_set, grid_size):
                if next_state not in reached:
                    reached.add(next_state)
                    frontier.append((next_state, path + [action]))

        return None

    def ucs_search(self, start_pos, goal_pos, walls, grid_size):
        """Return a least-cost action path using a priority queue."""
        start = tuple(start_pos)
        goal = tuple(goal_pos)
        wall_set = set(map(tuple, walls))

        # Every grid movement costs 1, but the frontier explicitly tracks
        # g(n), allowing UCS to expand the currently cheapest path first.
        frontier = [(0, start, [])]
        reached = {start: 0}
        self.last_expanded = 0

        while frontier:
            path_cost, state, path = heapq.heappop(frontier)

            # Ignore stale entries superseded by a cheaper route.
            if path_cost != reached[state]:
                continue
            if state == goal:
                return path

            self.last_expanded += 1
            for next_state, action in self._successors(
                    state, wall_set, grid_size):
                new_cost = path_cost + 1
                if (next_state not in reached
                        or new_cost < reached[next_state]):
                    reached[next_state] = new_cost
                    heapq.heappush(
                        frontier,
                        (new_cost, next_state, path + [action])
                    )

        return None

    def manhattan_distance(self, pos, goal):
        """Lower bound on unit-cost four-direction grid movement."""
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    def euclidean_distance(self, pos, goal):
        """Straight-line distance between two grid positions."""
        return math.sqrt((pos[0] - goal[0]) ** 2
                         + (pos[1] - goal[1]) ** 2)

    def astar_search(self, start_pos, goal_pos, walls, grid_size,
                     heuristic_type='manhattan'):
        """Return a shortest path, or None when the goal is unreachable.

        Both supplied heuristics are consistent for unit-cost four-way
        movement. Record best g costs to avoid duplicate frontier entries
        and discard stale routes before expanding a state.
        """
        heuristics = {
            'manhattan': self.manhattan_distance,
            'euclidean': self.euclidean_distance,
        }
        if heuristic_type not in heuristics:
            raise ValueError("heuristic_type must be 'manhattan' or 'euclidean'")
        heuristic = heuristics[heuristic_type]
        start, goal = tuple(start_pos), tuple(goal_pos)
        wall_set = set(map(tuple, walls))
        self.last_expanded = 0
        width, height = grid_size
        if any(pos in wall_set or not (0 <= pos[0] < width
                                      and 0 <= pos[1] < height)
               for pos in (start, goal)):
            return None

        frontier = []
        reached_states = set()
        best_cost = {start: 0}
        heapq.heappush(frontier, (heuristic(start, goal), 0, start, []))

        while frontier:
            f_cost, g_cost, current_pos, path_taken = heapq.heappop(frontier)
            if (current_pos in reached_states
                    or g_cost != best_cost[current_pos]):
                continue
            if current_pos == goal:
                return path_taken
            reached_states.add(current_pos)
            self.last_expanded += 1

            for next_pos, action in self._successors(
                    current_pos, wall_set, grid_size):
                if next_pos in reached_states:
                    continue
                new_g = g_cost + 1
                if new_g < best_cost.get(next_pos, math.inf):
                    best_cost[next_pos] = new_g
                    new_f = new_g + heuristic(next_pos, goal)
                    heapq.heappush(frontier, (
                        new_f, new_g, next_pos, path_taken + [action]))
        return None
