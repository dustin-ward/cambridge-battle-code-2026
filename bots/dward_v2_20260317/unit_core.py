import random

from cambc import Controller, Direction, EntityType, Environment, Position, EntityType

# non-centre directions
DIRECTIONS = [d for d in Direction if d != Direction.CENTRE]

def target_scale_cost(round) -> float:
    return (0.4 * round) + 150.0

def run_core(self):
    if self.c.get_scale_percent() < target_scale_cost(self.c.get_current_round()) and self.c.get_global_resources()[0] >= 500:
        spawn_pos = self.c.get_position().add(random.choice(DIRECTIONS))
        if self.c.can_spawn(spawn_pos):
            self.c.spawn_builder(spawn_pos)

