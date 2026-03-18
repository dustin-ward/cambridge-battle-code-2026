import random
import sys

from cambc import Controller, Direction, EntityType, Environment, Position, GameConstants
from unit_builder.astar import AStar

# non-centre directions
DIRECTIONS = [d for d in Direction if d != Direction.CENTRE]
CARD_DIRECTIONS = [Direction.NORTH, Direction.EAST,
                   Direction.SOUTH, Direction.WEST]
ORES = [Environment.ORE_TITANIUM, Environment.ORE_AXIONITE]


def builder_moveable_dir(self, builder_pos, target):
    """Given a non-cardinal direction, return a cardinal one that will eventually lead us to the target"""
    dir = builder_pos.direction_to(target)
    if dir in CARD_DIRECTIONS:
        return dir

    # Gross
    if dir == Direction.NORTHEAST:
        if self.c.can_move(Direction.NORTH):
            return Direction.NORTH
        return Direction.EAST
    if dir == Direction.NORTHWEST:
        if self.c.can_move(Direction.NORTH):
            return Direction.NORTH
        return Direction.WEST
    if dir == Direction.SOUTHEAST:
        if self.c.can_move(Direction.SOUTH):
            return Direction.SOUTH
        return Direction.EAST
    if dir == Direction.SOUTHWEST:
        if self.c.can_move(Direction.SOUTH):
            return Direction.SOUTH
        return Direction.WEST


def scan_surroundings(self):
    """
    Look at every tile in vision radius and note its type and the unit on it
    """
    nearby_tiles = self.c.get_nearby_tiles()
    for (x, y) in nearby_tiles:
        if self.map_mem[y][x] is None:
            self.map_mem[y][x] = {}

        self.map_mem[y][x]['Environment'] = self.c.get_tile_env((x, y))

        building_id = self.c.get_tile_building_id((x, y))
        self.map_mem[y][x]['building_id'] = building_id

        if building_id is not None:
            self.map_mem[y][x]['EntityType'] = self.c.get_entity_type(
                building_id)
            self.map_mem[y][x]['Team'] = self.c.get_team(building_id)


def builder_move(self, dir, build_conveyor=True) -> bool:
    """Try to move in dir direction. Return T/F if success/fail"""
    next_pos = self.c.get_position().add(dir)
    print(f'builder_move({dir},conv={build_conveyor}) -> {next_pos}')

    scan_surroundings(self)

    if build_conveyor and self.c.can_build_conveyor(next_pos, dir.opposite()):
        self.c.build_conveyor(next_pos, dir.opposite())

    if self.c.can_move(dir):
        self.c.move(dir)
        return True
    return False


def move_to_target(self, target_pos) -> bool:
    return True


def run_builder(self):
    # Initialize map
    if self.map_mem is None:
        self.map_mem = [[None for _ in range(self.map_height)]
                        for _ in range(self.map_width)]

    builder_pos = self.c.get_position(self.c.get_id())

    # KYS if on an enemy tile
    enemy_id = self.c.get_tile_building_id(builder_pos)
    if enemy_id is not None and self.c.get_team(enemy_id) is not self.c.get_team():
        self.c.self_destruct()
        return

    # Main behaviour
    if self.builder_searching:
        print('Searching...')

        # Find a vacant ORE tile
        nearby_tiles = self.c.get_nearby_tiles()
        for pos in nearby_tiles:
            tile = self.c.get_tile_env(pos)
            if tile not in ORES:
                continue

            if not self.c.is_tile_empty(pos):
                continue

            # Found one... get ready to move towards it
            print(f'Found empty ore at {pos}')
            self.builder_target_ore = pos
            path_finder = AStar(self.map_height, self.map_width, card=True)
            self.builder_target_path = path_finder.search(
                self.map_mem, builder_pos, pos)
            if len(self.builder_target_path) == 0:
                print('Couldn\'t find path')
                continue
            print(f'Path: {self.builder_target_path}')
            self.builder_searching = False
            break
        else:
            # Start exploring and placing conveyors in random direction
            if self.builder_search_dir is None:
                self.builder_search_dir = random.choice(CARD_DIRECTIONS)
            print(f'Searching {self.builder_search_dir}')

            if builder_move(self, self.builder_search_dir):
                print('Moved. Done Turn')
                return
            else:
                print('Cant move. Rotating')
                if random.choice([True, False]):
                    self.builder_search_dir = self.builder_search_dir.rotate_right().rotate_right()
                else:
                    self.builder_search_dir = self.builder_search_dir.rotate_left().rotate_left()

    else:
        print('Moving to target ore')

        # Is target ore within vision range?
        distance = builder_pos.distance_squared(self.builder_target_ore)
        if distance > GameConstants.BUILDER_BOT_VISION_RADIUS_SQ:
            print('Cant see target ore anymore. Ending Turn')
            self.builder_target_ore = None
            self.builder_target_path = None
            self.builder_searching = True
            return

        # Is target ore still vacant?
        if not self.c.is_tile_empty(self.builder_target_ore):
            print('Target ore not vacant anymore. Ending Turn')
            self.builder_target_ore = None
            self.builder_target_path = None
            self.builder_searching = True
            return

        # Is target ore within action range
        if distance <= 1:
            print(f'Distance={distance} <= 1')
            # Build harvestor
            if self.c.can_build_harvester(self.builder_target_ore):
                self.c.build_harvester(self.builder_target_ore)
                self.builder_mine_positions[self.builder_target_ore] = True
                self.builder_target_ore = None
                self.builder_target_path = None
                self.builder_searching = True
        else:
            # Move towards it
            print(f'Not close enough to ore. Distance={
                  distance} > 1')

            next_pos = self.builder_target_path[0]
            next_pos = Position(next_pos[1], next_pos[0])
            self.builder_target_path = self.builder_target_path[1:]
            dir = builder_pos.direction_to(next_pos)
            if builder_move(self, dir):
                print('Moved. Done Turn')
                return
            else:
                print('Cant move towards ore... Reset')
                self.builder_target_ore = None
                self.builder_target_path = None
                self.builder_searching = True
