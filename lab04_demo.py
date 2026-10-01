"""Repeatable Practical 04 checkpoints and a simulation without a GUI."""
from agent import SearchAgent
from visual_grid_game import VisualGridHuntGame


def main():
    agent = SearchAgent()
    print('Manhattan (0, 0) -> (3, 4):',
          agent.manhattan_distance((0, 0), (3, 4)))
    print('Euclidean (0, 0) -> (3, 4):',
          agent.euclidean_distance((0, 0), (3, 4)))
    print('\nSearch comparison: 20x20 open grid, (0, 0) -> (10, 0)')
    for name, search in [('BFS', agent.bfs_search), ('UCS', agent.ucs_search),
                         ('A* Manhattan', agent.astar_search),
                         ('A* Euclidean', lambda *args: agent.astar_search(
                             *args, heuristic_type='euclidean'))]:
        path = search((0, 0), (10, 0), [], (20, 20))
        print(f'{name}: {len(path)} moves, {agent.last_expanded} expanded nodes')

    env = VisualGridHuntGame(width=6, height=6, num_food=0,
                             num_opponents=0, custom_walls={(0, 1)})
    env.food_positions = {(0, 2), (3, 0), (5, 5)}
    env.toxic_traps = set()
    print('\nA* simulation: three food items, wall at (0, 1)')
    while not env.is_done():
        action = agent.sense_and_act(env.get_percept())
        env.execute_action(action)
        print(f'Step {env.steps:2}: {action:5} -> {tuple(env.agent_pos)}, '
              f'food remaining={len(env.food_positions)}, score={env.score}')
    print(f'Finished: {env.steps} steps, score={env.score}, '
          f'food remaining={len(env.food_positions)}')


if __name__ == '__main__':
    main()
