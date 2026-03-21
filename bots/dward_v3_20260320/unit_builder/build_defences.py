from cambc import Direction, Position, EntityType, GameConstants

import unit_builder.utils as ut


TURRET_DT = [
    (-2, -2, Direction.NORTHWEST),
    (2, -2, Direction.NORTHEAST),
    (2, 2, Direction.SOUTHEAST),
    (-2, 2, Direction.SOUTHWEST),
    (0, 2, Direction.SOUTH),
    (0, -2, Direction.NORTH),
]

FOUNDRY_DT = [
    (-2, 0),
    (2, 0),
]


def build_defences(self):
    print('STATE: Building Defences')

    if self.bldr_splitters_built < 8:
        build_splitters(self)
    elif self.bldr_turrets_built < 6:
        build_turrets(self)
    elif self.bldr_foundries_built < 2:
        build_foundries(self)
    else:
        self.bldr_state = ut.State.EXPLORING
        return


def build_splitters(self):
    print('need to build a splitter')

    for pos, dir in ut.get_splitter_locations(self):
        if ut.is_splitter(self, pos):
            continue
        print(f'trying to build splitter at: {pos}')

        # Remove any roads
        if ut.is_road(self, pos):
            if self.c.can_destroy(pos):
                self.c.destroy(pos)

        dis = self.c.get_position().distance_squared(pos)
        if dis > GameConstants.ACTION_RADIUS_SQ:
            next_pos = self.c.get_position().add(self.c.get_position().direction_to(pos))
            if not ut.builder_move(self, next_pos, scan=False):
                return

        dis = self.c.get_position().distance_squared(pos)
        if dis <= GameConstants.ACTION_RADIUS_SQ:
            if self.c.can_build_splitter(pos, dir):
                self.c.build_splitter(pos, dir)
                self.bldr_splitters_built += 1
            else:
                print(f'couldn\'t build splitter at {pos}')
                return


def build_turrets(self):
    print('need to build a turret')

    for dx, dy, dir in TURRET_DT:
        x, y = self.core_pos
        x += dx
        y += dy
        pos = Position(x, y)
        if self.c.get_position().distance_squared(pos) > GameConstants.BUILDER_BOT_VISION_RADIUS_SQ or ut.is_sentinel(self, pos):
            continue
        print(f'trying to build sentinel at: {pos}')

        # Remove any roads
        if ut.is_road(self, pos):
            if self.c.can_destroy(pos):
                self.c.destroy(pos)

        dis = self.c.get_position().distance_squared(pos)
        if dis > GameConstants.ACTION_RADIUS_SQ:
            next_pos = self.c.get_position().add(self.c.get_position().direction_to(pos))
            if not ut.builder_move(self, next_pos, scan=False):
                return

        dis = self.c.get_position().distance_squared(pos)
        if dis <= GameConstants.ACTION_RADIUS_SQ:
            if self.c.can_build_sentinel(pos, dir):
                self.c.build_sentinel(pos, dir)
                self.bldr_turrets_built += 1
            else:
                print(f'couldn\'t build sentinel at {pos}')
                return


def build_foundries(self):
    print('need to build a foundary')

    # Wait for enough money
    if self.c.get_global_resources()[0] < 1000:
        return

    for dx, dy in FOUNDRY_DT:
        x, y = self.core_pos
        x += dx
        y += dy
        pos = Position(x, y)
        if ut.is_foundry(self, pos):
            continue
        print(f'trying to build foundry at: {pos}')

        # Remove any roads
        if ut.is_road(self, pos):
            if self.c.can_destroy(pos):
                self.c.destroy(pos)

        dis = self.c.get_position().distance_squared(pos)
        if dis > GameConstants.ACTION_RADIUS_SQ:
            next_pos = self.c.get_position().add(self.c.get_position().direction_to(pos))
            if not ut.builder_move(self, next_pos, scan=False):
                return

        dis = self.c.get_position().distance_squared(pos)
        if dis <= GameConstants.ACTION_RADIUS_SQ:
            if self.c.can_build_foundry(pos):
                self.c.build_foundry(pos)
                self.bldr_foundries_built += 1
            else:
                print(f'couldn\'t build foundry at {pos}')
                return
