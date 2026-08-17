# agent.py
import random


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