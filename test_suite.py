import unittest
import random
from agent import SimpleReflexAgent, ModelBasedAgent, SearchAgent


class TestPractical1And2_ReflexAgents(unittest.TestCase):
    """
    Tests for Practicals 1 & 2: Simple Reflex and Model-Based Agents.
    Focuses on Condition-Action rules, partial observability, and memory.
    """

    def setUp(self):
        # Instantiate agents (assuming students have created these classes)
        try:
            self.simple_agent = SimpleReflexAgent()
            self.model_agent = ModelBasedAgent()
        except NameError:
            self.fail("Agent classes not found. Ensure SimpleReflexAgent and ModelBasedAgent are defined.")

    def test_simple_reflex_logic(self):
        """Test 1: Simple Reflex Agent should react purely to immediate percepts."""
        # Scenario A: Food is present -> Agent should want to collect/stay/move appropriately
        percept_food = {'wall_ahead': False, 'food_here': True}
        action = self.simple_agent.sense_and_act(percept_food)
        self.assertIsNotNone(action, "SimpleReflexAgent returned None instead of an action.")

        # Scenario B: Wall is ahead -> Agent must turn or change direction
        percept_wall = {'wall_ahead': True, 'food_here': False}
        action_wall = self.simple_agent.sense_and_act(percept_wall)
        self.assertIn(action_wall, ['Left', 'Right', 'Down', 'Up'],
                      "Agent did not output a valid movement action when facing a wall.")

    def test_model_based_memory(self):
        """Test 2: Model-Based Agent should maintain internal state to escape loops."""
        # Feed the exact same percept twice to simulate being stuck in a corner
        percept = {'wall_ahead': True, 'food_here': False}

        action_1 = self.model_agent.sense_and_act(percept)
        action_2 = self.model_agent.sense_and_act(percept)

        # A simple reflex agent would return the exact same action twice.
        # A model-based agent should remember the previous failure and try a DIFFERENT action.
        self.assertNotEqual(
            action_1,
            action_2,
            "ModelBasedAgent returned the exact same action twice in a row for the same percept. Internal state/memory is not working correctly."
        )


class TestPractical3_SearchAgent(unittest.TestCase):
    """
    Tests for Practical 3: Problem-Solving Agents.
    Focuses on offline planning and Breadth-First Search (BFS) implementation.
    """

    def setUp(self):
        try:
            self.search_agent = SearchAgent()
        except NameError:
            self.fail("SearchAgent class not found.")

    def test_bfs_shortest_path(self):
        """Test 3: BFS must find the optimal (shortest) path in a static maze."""
        # Mock Environment Data
        grid_size = (4, 4)
        start_pos = (0, 0)
        goal_pos = (3, 3)

        # Create a U-shaped wall trap that the agent must navigate around
        # Grid layout (S=Start, G=Goal, W=Wall):
        # 3 | . . . G
        # 2 | W W W .
        # 1 | . . . .
        # 0 | S W W .
        #   ---------
        #     0 1 2 3
        walls = [(1, 0), (2, 0), (0, 2), (1, 2), (2, 2)]

        # Run student's BFS algorithm
        try:
            path = self.search_agent.bfs_search(start_pos, goal_pos, walls, grid_size)
        except AttributeError:
            self.fail("bfs_search method not implemented in SearchAgent.")

        # Verify the path is valid and optimal
        self.assertIsNotNone(path, "BFS returned None. No path found.")
        self.assertIsInstance(path, list, "BFS should return a list of actions (strings).")

        # The shortest path taking Manhattan distance around these specific walls is exactly 6 steps.
        # Path: Up -> Right -> Right -> Right -> Up -> Up
        self.assertEqual(len(path), 6, f"BFS did not find the optimal path. Expected 6 steps, got {len(path)}.")

    def test_bfs_unreachable_goal(self):
        """Test 4: BFS must correctly return failure (None/Empty) if goal is blocked."""
        grid_size = (3, 3)
        start_pos = (0, 0)
        goal_pos = (2, 2)

        # Box the goal in completely
        walls = [(1, 2), (2, 1), (1, 1)]

        path = self.search_agent.bfs_search(start_pos, goal_pos, walls, grid_size)

        # The agent should realize it's impossible and return None or an empty list
        is_empty_or_none = (path is None) or (len(path) == 0)
        self.assertTrue(is_empty_or_none, "BFS should return None or [] when the goal is unreachable.")


class TestPractical4_AStar(unittest.TestCase):
    def setUp(self):
        self.agent = SearchAgent()

    def assert_valid_path(self, start, goal, walls, size, path):
        self.assertIsNotNone(path)
        pos = start
        moves = dict(self.agent._MOVES)
        for action in path:
            dx, dy = moves[action]
            pos = (pos[0] + dx, pos[1] + dy)
            self.assertNotIn(pos, walls)
            self.assertTrue(0 <= pos[0] < size[0] and 0 <= pos[1] < size[1])
        self.assertEqual(pos, goal)

    def test_heuristic_checkpoint(self):
        self.assertEqual(self.agent.manhattan_distance((0, 0), (3, 4)), 7)
        self.assertEqual(self.agent.euclidean_distance((0, 0), (3, 4)), 5.0)
        self.assertEqual(self.agent.manhattan_distance((3, 4), (0, 0)), 7)

    def test_astar_matches_bfs_on_seeded_mazes(self):
        rng = random.Random(4)
        for trial in range(30):
            walls = {(x, y) for x in range(8) for y in range(8)
                     if (x, y) not in ((0, 0), (7, 7)) and rng.random() < 0.3}
            reference = self.agent.bfs_search((0, 0), (7, 7), walls, (8, 8))
            for heuristic in ('manhattan', 'euclidean'):
                with self.subTest(trial=trial, heuristic=heuristic):
                    path = self.agent.astar_search(
                        (0, 0), (7, 7), walls, (8, 8), heuristic)
                    if reference is None:
                        self.assertIsNone(path)
                    else:
                        self.assertEqual(len(path), len(reference))
                        self.assert_valid_path((0, 0), (7, 7), walls, (8, 8), path)

    def test_edge_cases(self):
        for heuristic in ('manhattan', 'euclidean'):
            self.assertEqual(self.agent.astar_search(
                (0, 0), (0, 0), [], (3, 3), heuristic), [])
            self.assertIsNone(self.agent.astar_search(
                (0, 0), (2, 2), [(1, 2), (2, 1)], (3, 3), heuristic))
            self.assertIsNone(self.agent.astar_search(
                (0, 0), (2, 2), [(2, 2)], (3, 3), heuristic))
        with self.assertRaises(ValueError):
            self.agent.astar_search((0, 0), (1, 1), [], (2, 2), 'unknown')

    def test_decision_loop_skips_unreachable_food(self):
        percept = {'all_food': [(0, 2), (3, 0)],
                   'walls': [(0, 1), (1, 2), (0, 3)], 'grid_size': (4, 4)}
        self.assertEqual(self.agent.sense_and_act(percept), 'Right')

    def test_astar_collects_all_food_in_environment(self):
        from visual_grid_game import VisualGridHuntGame
        env = VisualGridHuntGame(width=6, height=6, num_food=0,
                                 num_opponents=0, custom_walls={(0, 1)})
        env.food_positions = {(0, 2), (3, 0), (5, 5)}
        env.toxic_traps = set()
        while not env.is_done():
            env.execute_action(self.agent.sense_and_act(env.get_percept()))
            self.assertEqual(tuple(env.agent_pos), self.agent.current_pos)
        self.assertEqual(env.food_positions, set())
        self.assertEqual(env.score, 60)


if __name__ == '__main__':
    # Run the test suite
    print("=== IT3012: Intelligent Agents - Autograder Test Suite ===\n")
    unittest.main(verbosity=2)
