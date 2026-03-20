import random

from cambc import Position

# from unit_builder.astar import AStar
from unit_builder.naive_pathfinder import NaivePathfinder
import unit_builder.utils as ut


def exploring(self):
    """
    'Default' state for a builder unit.
    The builder should pick a random location it hasn't seen before, and travel towards it.
    Depending on what it finds, a new state or 'mission' can be derived
    """
    print('STATE: Exploring...')

    # On first turn, take note of the coords for the core
    if self.core_pos is None:
        self.core_pos = ut.get_center_of_core(self, self.c.get_position())
        print(f'Found center of core at: {self.core_pos}')

    for pos in self.c.get_nearby_tiles():
        if pos == self.c.get_position() or pos in self.bldr_exp_ignore:
            # Ignore center or 'ignore' tiles
            continue

        is_ore = False
        is_vacant = True

        env = self.c.get_tile_env(pos)
        if env in ut.ORES:
            print(f'Found ore at {pos}: {env}')
            is_ore = True

        building_id = self.c.get_tile_building_id(pos)
        if building_id is not None:
            # ent = self.c.get_entity_type(building_id)
            is_vacant = False
            # print(f'Found building at {pos}: {ent}')

        builder_id = self.c.get_tile_builder_bot_id(pos)
        if builder_id is not None:
            # ent = self.c.get_entity_type(builder_id)
            # enemy = self.c.get_team(builder_id) != self.c.get_team()
            is_vacant = False
            # print(f'Found builder bot at {pos}: {ent} enemy={enemy}')

        # Switch to mine mode
        if is_ore and is_vacant:
            self.bldr_state = ut.State.BUILDING_MINE
            self.bldr_tgt_pos = pos
            self.bldr_tgt_pth = None
            return

    # Path empty. Choose a new location
    if self.bldr_tgt_pth is not None and len(self.bldr_tgt_pth) == 0:
        self.bldr_tgt_pos = None
        self.bldr_tgt_pth = None

    # Choose a position on the boundary of this bots known map
    if self.bldr_tgt_pos is None:
        ut.scan_surroundings(self)
        if len(self.vsn_bndry) > 0:
            self.bldr_tgt_pos = random.choice(list(self.vsn_bndry))
        else:
            self.bldr_tgt_pos = Position(random.randint(0, self.map_width - 1), random.randint(0, self.map_height - 1))
        print(f'Move to: {self.bldr_tgt_pos}')

    if self.bldr_tgt_pth is None:
        pathfinder = NaivePathfinder(self.map_height, self.map_width)
        self.bldr_tgt_pth = pathfinder.search(self.map_mem, self.c.get_position(), self.bldr_tgt_pos)
        print(f'Path: {self.bldr_tgt_pth}')
        if len(self.bldr_tgt_pth) == 0:
            self.bldr_tgt_pos = None
            self.bldr_tgt_pth = None

    # Move along path
    next_pos = self.bldr_tgt_pth[0]
    next_pos = Position(next_pos[1], next_pos[0])
    self.bldr_tgt_pth = self.bldr_tgt_pth[1:]

    if not ut.builder_move(self, next_pos):
        self.bldr_tgt_pos = None
        self.bldr_tgt_pth = None
        return False

    return True

