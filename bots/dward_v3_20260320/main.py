from cambc import Controller, EntityType, Position

from unit_core import run_core
import unit_builder


class Player:
    def __init__(self):
        self.c = None                       # Reference to controller object
        self.map_height: int = -1
        self.map_width: int = -1
        self.map_mem: list[list] = None     # This units memory of every tile its seen
        self.vsn_bndry: set = set()         # Set of positions that form the boundary of tiles that this unit has seen
        self.core_pos: Position = None      # Center position of the core

        # CORE
        self.num_spawned: int = 0               # Number of builders spawned by core
        self.prev_cost_scale: float = 100.0     # Cost scale from last turn

        # BUILDER
        self.bldr_state: unit_builder.State = unit_builder.utils.State.EXPLORING
        self.bldr_failed_mvmt: int = 0          # Number of failed movement attempts
        self.bldr_tgt_pos: Position = None      # Position on the map to move towards
        self.bldr_tgt_pth: list[tuple] = None   # Path to the target position
        self.bldr_exp_ignore: set = set()       # Positions to ignore during exploration phase
        self.bldr_mine_built: bool = False      # Has the harvester been built yet in mining phase?
        self.bldr_brdg_prv: Position = None     # Previous connection point for a bridge sequence

    def run(self, ct: Controller) -> None:

        self.map_height = ct.get_map_height()
        self.map_width = ct.get_map_width()

        self.c = ct
        etype = ct.get_entity_type()
        if etype == EntityType.CORE:
            run_core(self)
        elif etype == EntityType.BUILDER_BOT:
            unit_builder.run_builder(self)
