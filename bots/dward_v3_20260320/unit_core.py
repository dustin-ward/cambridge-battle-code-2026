import random

from cambc import Direction, Position

# non-centre directions
DIRECTIONS = [d for d in Direction if d != Direction.CENTRE]


def spawn_builder(self, pos: Position = None):
    if pos is None:
        pos = self.c.get_position().add(random.choice(DIRECTIONS))
    if self.c.can_spawn(pos):
        self.c.spawn_builder(pos)
        print(f'spawned builder at {pos}')
        return True
    else:
        print(f'can\'t spawn builder at {pos}')
        return False


def run_core(self):
    if not self.core_spawned_defence:
        marker_pos = self.c.get_position().add(Direction.NORTH).add(Direction.NORTH)
        if self.c.can_place_marker(marker_pos):
            self.c.place_marker(marker_pos, 7777)
        if spawn_builder(self, self.c.get_position().add(Direction.NORTH)):
            self.core_spawned_defence = True

    cur_scale_pct = self.c.get_scale_percent()
    print(f'Current cost scale: {cur_scale_pct} prev: {self.prev_cost_scale}')
    if self.prev_cost_scale - cur_scale_pct > 9.0:
        spawn_builder(self)

    if self.core_num_spawned < 5:
        spawn_builder(self)
        self.core_num_spawned += 1

    self.prev_cost_scale = cur_scale_pct

