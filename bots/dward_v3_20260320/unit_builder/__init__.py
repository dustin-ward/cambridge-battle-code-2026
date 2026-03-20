from unit_builder.exploring import exploring
from unit_builder.build_mine import build_mine
import unit_builder.utils as ut


def run_builder(self):
    # Initialize map
    if self.map_mem is None:
        self.map_mem = [[None for _ in range(self.map_height)]
                        for _ in range(self.map_width)]

    # Main behaviour
    if self.bldr_state == ut.State.EXPLORING:
        exploring(self)
    elif self.bldr_state == ut.State.BUILDING_MINE:
        build_mine(self)
    else:
        pass
