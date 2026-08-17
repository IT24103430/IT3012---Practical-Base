# simulator.py
from visual_grid_game import VisualGridHuntGame
from agent import SimpleReflexAgent, ModelBasedAgent


def run_agent(agent_class, max_steps=15, custom_walls=None):
    """Runs a single agent against a fresh VisualGridHuntGame environment,
    printing the percept/action/position at every step."""

    # A small corner-trap grid: a wall directly above the agent's start
    # position forces it into the classic 'bounce' scenario from Lab 02.
    if custom_walls is None:
        custom_walls = {(0, 1)}

    env = VisualGridHuntGame(width=4, height=4, num_food=3, num_opponents=0,
                              custom_walls=custom_walls)
    agent = agent_class()

    print(f"=== IT3012 Lab 02 - {agent_class.__name__} Simulation Started ===")
    steps_taken = 0
    while not env.is_done() and steps_taken < max_steps:
        percept = env.get_percept()
        action = agent.sense_and_act(percept)
        env.execute_action(action)
        steps_taken += 1

        print(f"Step {steps_taken:>2} | Pos: {tuple(env.agent_pos)} | Facing: {env.facing} | "
              f"Action: {action:<6} | wall_ahead={percept['wall_ahead']} "
              f"food_here={percept['food_here']} | Score: {env.score}")

    print(f"\n{'Game Over!' if env.is_done() else 'Step limit reached (still stuck?)'} "
          f"Final Score: {env.score} after {env.steps} real environment steps.\n")


if __name__ == "__main__":
    # --- Step 1.2: Watch the Simple Reflex Agent get trapped ---
    run_agent(SimpleReflexAgent)

    # --- Step 1.3: Watch the Model-Based Agent remember and escape ---
    run_agent(ModelBasedAgent)