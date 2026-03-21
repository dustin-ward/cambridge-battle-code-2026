from unit_builder.exploring import exploring
from unit_builder.build_mine import build_mine
from unit_builder.build_defences import build_defences
import unit_builder.utils as ut


def run_builder(self):
    # Initialize map
    if self.map_mem is None:
        self.map_mem = [[None for _ in range(self.map_width)]
                        for _ in range(self.map_height)]

    # Main behaviour
    if self.bldr_state == ut.State.EXPLORING:
        exploring(self)
    elif self.bldr_state == ut.State.BUILDING_MINE:
        build_mine(self)
    elif self.bldr_state == ut.State.BUILDING_DEFENCE:
        build_defences(self)
    else:
        pass
