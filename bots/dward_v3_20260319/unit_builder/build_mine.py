from cambc import GameConstants, Position

from unit_builder.naive_pathfinder import NaivePathfinder
import unit_builder.utils as ut


def build_mine(self):

    if self.bldr_mine_built:
        # print(f'unable to build harvester at {self.bldr_ore_tgt}')
        self.bldr_ore_tgt = None
        self.bldr_ore_pth = None
        self.bldr_state = ut.State.EXPLORING
        return False
    else:
        distance = self.c.get_position().distance_squared(self.bldr_ore_tgt)
        if distance <= GameConstants.ACTION_RADIUS_SQ:
            if self.c.can_build_harvester(self.bldr_ore_tgt):
                self.c.build_harvester(self.bldr_ore_tgt)
                self.bldr_mine_built = True
                print(f'built harvester at {self.bldr_ore_tgt}')
            else:
                print(f'unable to build harvester at {self.bldr_ore_tgt}')
                self.bldr_ore_tgt = None
                self.bldr_ore_pth = None
                self.bldr_state = ut.State.EXPLORING
                return False
        else:
            if self.bldr_ore_pth is None:
                pathfinder = NaivePathfinder(self.map_height, self.map_width)
                self.bldr_ore_pth = pathfinder.search(self.map_mem, self.c.get_position(), self.bldr_ore_tgt)

            if len(self.bldr_ore_pth) == 0:
                print(f'unable to find path to {self.bldr_ore_tgt}')
                self.bldr_ore_tgt = None
                self.bldr_ore_pth = None
                self.bldr_state = ut.State.EXPLORING
                return False

            next_pos = self.bldr_ore_pth[0]
            next_pos = Position(next_pos[1], next_pos[0])
            self.bldr_ore_pth = self.bldr_ore_pth[1:]

            if not ut.builder_move(self, next_pos):
                print(f'blocked path to {self.bldr_ore_tgt}')
                self.bldr_ore_tgt = None
                self.bldr_ore_pth = None
                self.bldr_state = ut.State.EXPLORING
                return False
