from cambc import Controller, Direction, EntityType, Environment, Position

from unit_core import run_core
import unit_builder

class Player:
    def __init__(self):
        self.c = None
        self.map_height: int = -1
        self.map_width: int = -1
        self.map_mem: list[list] = None

        # CORE
        self.num_spawned = 0  # number of builder bots spawned so far (core)

        # BUILDER
        self.builder_searching: bool = True
        self.builder_search_dir: Direction = None
        self.builder_target_ore: Position = None
        self.builder_target_path: list[tuple] = None

        self.builder_mine_positions: dict = {}

    def run(self, ct: Controller) -> None:

        self.map_height = ct.get_map_height()
        self.map_width = ct.get_map_width()

        self.c = ct
        etype = ct.get_entity_type()
        if etype == EntityType.CORE:
            run_core(self)
        elif etype == EntityType.BUILDER_BOT:
            unit_builder.run_builder(self)

        print(f'CPU TIME: {ct.get_cpu_time_elapsed()}')
