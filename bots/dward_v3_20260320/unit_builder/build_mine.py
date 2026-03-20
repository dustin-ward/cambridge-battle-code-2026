from cambc import GameConstants, Position

from unit_builder.astar import AStar
from unit_builder.naive_pathfinder import NaivePathfinder
import unit_builder.utils as ut


def build_mine(self):
    print('STATE: Mining')

    self.bldr_exp_ignore = set()

    keep_state = True
    if self.bldr_mine_built:
        keep_state = transport_to_core(self)
    else:
        keep_state = travel_to_ore(self)

    # Go back to explore mode
    if not keep_state:
        self.bldr_tgt_pos = None
        self.bldr_tgt_pth = None
        self.bldr_failed_mvmt = 0
        self.bldr_mine_built = False
        self.bldr_brdg_prv = None
        self.bldr_state = ut.State.EXPLORING
        return False

    return True


def travel_to_ore(self):
    """
    Given a target position that has a _presumably_ vacant ore, travel towards it and build a harvester.

    Uses naive pathfinding at first, and allows for 1 retry with A* if it fails to follow the naive path
    """

    # If we are close enough to the ore try to build the harvester
    # Otherwise move closer...
    distance = self.c.get_position().distance_squared(self.bldr_tgt_pos)
    if distance <= GameConstants.ACTION_RADIUS_SQ:
        if self.c.can_build_harvester(self.bldr_tgt_pos):
            self.c.build_harvester(self.bldr_tgt_pos)
            self.bldr_mine_built = True
            print(f'built harvester at {self.bldr_tgt_pos}')

            # Set the start of the bridge sequence to be current space
            # Then start building back towards the core
            # TODO: Pick an optimal tile here
            self.bldr_brdg_prv = self.c.get_position()
            self.bldr_tgt_pos = self.core_pos
            self.bldr_tgt_pth = None
            return True
        else:
            print(f'unable to build harvester at {self.bldr_tgt_pos}')
            return False

    else:
        # Need a path to ore
        if self.bldr_tgt_pth is None:
            # First try is naive, then try with A*
            if self.bldr_failed_mvmt == 0:
                pathfinder = NaivePathfinder(self.map_height, self.map_width)
            else:
                pathfinder = AStar(self.map_height, self.map_width)
            self.bldr_tgt_pth = pathfinder.search(self.map_mem, self.c.get_position(), self.bldr_tgt_pos)

        # No path available. Give up
        if len(self.bldr_tgt_pth) == 0:
            print(f'unable to find path to {self.bldr_tgt_pos}')
            self.bldr_exp_ignore.add(self.bldr_tgt_pos)
            return False

        # Move to next pos on path
        next_pos = ut.yx_to_pos(self.bldr_tgt_pth[0])
        self.bldr_tgt_pth = self.bldr_tgt_pth[1:]

        if not ut.builder_move(self, next_pos):
            print(f'blocked path to {self.bldr_tgt_pos}')
            self.bldr_tgt_pth = None

            self.bldr_failed_mvmt += 1
            if self.bldr_failed_mvmt > 1:
                # Failed to find path with both pathfinders. Give up
                return False

    return True

# BRIDGE RADIUS
# d^2 <= 9
#       X
#     XX.XX
#     X...X
#    X..O..X
#     X...X
#     XX.XX
#       X


def transport_to_core(self):
    print(f'transporting back to core. brdg_prv: {self.bldr_brdg_prv}')

    # Figure out how to get back to the core
    if self.bldr_tgt_pth is None:
        pathfinder = AStar(self.map_height, self.map_width)
        self.bldr_tgt_pth = pathfinder.search(self.map_mem, self.c.get_position(), self.core_pos)

    # Couldn't find path...
    if not self.bldr_tgt_pth:
        print(f'couldn\'t find a path back to the core from {self.c.get_position()}')
        return False

    # Is the end of the previous bridge segment within action range?
    prv_brdg_end_dis = self.c.get_position().distance_squared(self.bldr_brdg_prv)
    if prv_brdg_end_dis <= GameConstants.ACTION_RADIUS_SQ:
        # Destroy any building in the way
        # I hope this is a road...
        if self.c.can_destroy(self.bldr_brdg_prv):
            self.c.destroy(self.bldr_brdg_prv)

        # Going to build a bridge. Find where it should end
        pth_idx = 3
        brdg_len = 0
        while pth_idx > 0:
            if pth_idx >= len(self.bldr_tgt_pth):
                pth_idx -= 1
                continue
            brdg_end = ut.yx_to_pos(self.bldr_tgt_pth[pth_idx])
            brdg_len = self.bldr_brdg_prv.distance_squared(brdg_end)
            if brdg_len > GameConstants.BRIDGE_TARGET_RADIUS_SQ:
                pth_idx -= 1
                continue
            if brdg_end == self.core_pos:
                pth_idx -= 1
                continue
            break

        assert brdg_len <= GameConstants.BRIDGE_TARGET_RADIUS_SQ, 'invalid bridge target on path'

        if self.c.can_build_bridge(self.bldr_brdg_prv, brdg_end) and ut.can_afford(self, GameConstants.BRIDGE_BASE_COST):
            self.c.build_bridge(self.bldr_brdg_prv, brdg_end)
            self.bldr_brdg_prv = brdg_end

            if ut.is_core(self, brdg_end):
                # Finished! Go back to exploring
                return False
        else:
            # Try again?
            return True

    # Move to next pos on path
    # Don't move if we built a bridge. Just in case we need to place a road
    next_pos = ut.yx_to_pos(self.bldr_tgt_pth[0])
    if self.c.get_action_cooldown() > 0 and not self.c.is_tile_passable(next_pos):
        return True
    self.bldr_tgt_pth = self.bldr_tgt_pth[1:]

    if not ut.builder_move(self, next_pos):
        print(f'blocked path to {self.bldr_tgt_pos}')
        self.bldr_tgt_pth = None

        self.bldr_failed_mvmt += 1
        if self.bldr_failed_mvmt > 3:
            # Failed to find path 3 times. Give up
            return False

    return True
