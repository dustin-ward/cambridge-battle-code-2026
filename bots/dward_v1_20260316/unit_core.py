import random

from cambc import Controller, Direction, EntityType, Environment, Position, EntityType

# non-centre directions
DIRECTIONS = [d for d in Direction if d != Direction.CENTRE]


def run_core(self, ct: Controller):
    if self.num_spawned < 10:
        spawn_pos = ct.get_position().add(random.choice(DIRECTIONS))
        if ct.can_spawn(spawn_pos):
            ct.spawn_builder(spawn_pos)
            self.num_spawned += 1

