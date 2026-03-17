import random

from cambc import Controller, Direction, EntityType, Environment, Position, EntityType

# non-centre directions
DIRECTIONS = [d for d in Direction if d != Direction.CENTRE]

def target_scale_cost(round) -> float:
    return (0.4 * round) + 150.0

def run_core(self, ct: Controller):
    if ct.get_scale_percent() < target_scale_cost(ct.get_current_round()) and ct.get_global_resources()[0] >= 500:
        spawn_pos = ct.get_position().add(random.choice(DIRECTIONS))
        if ct.can_spawn(spawn_pos):
            ct.spawn_builder(spawn_pos)

