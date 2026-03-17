from cambc import Controller, Direction, EntityType, Environment, Position

from unit_core import run_core
from unit_builder import run_builder


class Player:
    def __init__(self):
        # CORE
        self.num_spawned = 0  # number of builder bots spawned so far (core)

        # BUILDER
        self.builder_searching: bool = True
        self.builder_search_dir: Direction = None
        self.builder_target_ore: Position = None

        self.builder_mine_positions: dict = {}

    def run(self, ct: Controller) -> None:
        etype = ct.get_entity_type()
        if etype == EntityType.CORE:
            run_core(self, ct)
        elif etype == EntityType.BUILDER_BOT:
            run_builder(self, ct)
