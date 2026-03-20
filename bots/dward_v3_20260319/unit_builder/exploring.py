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
    print('Exploring...')

    ores = []
    for pos in self.c.get_nearby_tiles():
        env = self.c.get_tile_env(pos)
        if env in ut.ORES:
            print(f'Found ore at {pos}: {env}')
            ores.append(pos)

        building_id = self.c.get_tile_building_id(pos)
        if building_id is not None:
            ent = self.c.get_entity_type(building_id)
            print(f'Found building at {pos}: {ent}')

        builder_id = self.c.get_tile_builder_bot_id(pos)
        if builder_id is not None:
            ent = self.c.get_entity_type(builder_id)
            enemy = self.c.get_team(builder_id) != self.c.get_team()
            print(f'Found builder bot at {pos}: {ent} enemy={enemy}')

    # Switch to mine mode
    if len(ores) > 0:
        self.bldr_state = ut.State.BUILDING_MINE
        self.bldr_exp_pos = None
        self.bldr_exp_pth = None
        self.bldr_ore_tgt = ores[0]
        return

    # Path empty. Choose a new location
    if self.bldr_exp_pth is not None and len(self.bldr_exp_pth) == 0:
        self.bldr_exp_pos = None
        self.bldr_exp_pth = None

    # Choose a position on the boundary of this bots known map
    if self.bldr_exp_pos is None:
        ut.scan_surroundings(self)
        self.bldr_exp_pos = random.choice(list(self.bldr_vsn_bndry))
        print(f'Move to: {self.bldr_exp_pos}')

    if self.bldr_exp_pth is None:
        # pathfinder = AStar(self.map_height, self.map_width)
        pathfinder = NaivePathfinder(self.map_height, self.map_width)
        self.bldr_exp_pth = pathfinder.search(self.map_mem, self.c.get_position(), self.bldr_exp_pos)
        print(f'Path: {self.bldr_exp_pth}')
        if len(self.bldr_exp_pth) == 0:
            self.bldr_exp_pos = None
            self.bldr_exp_pth = None

    # Move along path
    next_pos = self.bldr_exp_pth[0]
    next_pos = Position(next_pos[1], next_pos[0])
    self.bldr_exp_pth = self.bldr_exp_pth[1:]

    if not ut.builder_move(self, next_pos):
        self.bldr_exp_pos = None
        self.bldr_exp_pth = None
        return False

    return True
