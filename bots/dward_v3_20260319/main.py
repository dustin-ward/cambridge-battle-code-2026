from cambc import Controller, EntityType, Position

from unit_core import run_core
import unit_builder


class Player:
    def __init__(self):
        self.c = None
        self.num_spawned: int = 0
        self.map_height: int = -1
        self.map_width: int = -1
        self.map_mem: list[list] = None
        self.core_pos: Position = None

        # BUILDER
        self.bldr_state: unit_builder.State = unit_builder.utils.State.EXPLORING
        self.bldr_exp_pos: Position = None
        self.bldr_exp_pth: list[tuple] = None
        self.bldr_vsn_bndry: set = set()
        self.bldr_ore_tgt: Position = None
        self.bldr_ore_pth: list[tuple] = None
        self.bldr_mine_built: bool = False

    def run(self, ct: Controller) -> None:

        self.map_height = ct.get_map_height()
        self.map_width = ct.get_map_width()

        self.c = ct
        etype = ct.get_entity_type()
        if etype == EntityType.CORE:
            run_core(self)
        elif etype == EntityType.BUILDER_BOT:
            unit_builder.run_builder(self)
