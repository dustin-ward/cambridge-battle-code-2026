import random

from cambc import Controller, Direction, EntityType, Environment, Position, GameConstants

# non-centre directions
DIRECTIONS = [d for d in Direction if d != Direction.CENTRE]
CARD_DIRECTIONS = [Direction.NORTH, Direction.EAST,
                   Direction.SOUTH, Direction.WEST]
ORES = [Environment.ORE_TITANIUM, Environment.ORE_AXIONITE]


def builder_moveable_dir(ct: Controller, builder_pos, target):
    """Given a non-cardinal direction, return a cardinal one that will eventually lead us to the target"""
    dir = builder_pos.direction_to(target)
    if dir in CARD_DIRECTIONS:
        return dir

    # Gross
    if dir == Direction.NORTHEAST:
        if ct.can_move(Direction.NORTH):
            return Direction.NORTH
        return Direction.EAST
    if dir == Direction.NORTHWEST:
        if ct.can_move(Direction.NORTH):
            return Direction.NORTH
        return Direction.WEST
    if dir == Direction.SOUTHEAST:
        if ct.can_move(Direction.SOUTH):
            return Direction.SOUTH
        return Direction.EAST
    if dir == Direction.SOUTHWEST:
        if ct.can_move(Direction.SOUTH):
            return Direction.SOUTH
        return Direction.WEST


def builder_move(ct: Controller, dir, build_conveyor=True) -> bool:
    """Try to move in dir direction. Return T/F if success/fail"""
    move_pos = ct.get_position().add(dir)
    print(f'builder_move({dir},conv={build_conveyor}) -> {move_pos}')

    if build_conveyor and ct.can_build_conveyor(move_pos, dir.opposite()):
        ct.build_conveyor(move_pos, dir.opposite())

    if ct.can_move(dir):
        ct.move(dir)
        return True
    return False


def run_builder(self, ct: Controller):
    builder_pos = ct.get_position(ct.get_id())

    # KYS if on an enemy tile
    # enemy_id = ct.get_tile_building_id(builder_pos)
    # if enemy_id is not None and ct.get_team(enemy_id) is not ct.get_team():
        # ct.self_destruct()

    # Main behaviour
    if self.builder_searching:
        print('Searching...')

        # Find a vacant ORE tile
        nearby_tiles = ct.get_nearby_tiles()
        for pos in nearby_tiles:
            tile = ct.get_tile_env(pos)
            if tile not in ORES:
                continue

            if not ct.is_tile_empty(pos):
                continue

            # Found one... get ready to move towards it
            print(f'Found empty ore at {pos}')
            self.builder_target_ore = pos
            self.builder_searching = False
            break
        else:
            # Start exploring and placing conveyors in random direction
            if self.builder_search_dir is None:
                self.builder_search_dir = random.choice(CARD_DIRECTIONS)
            print(f'Searching {self.builder_search_dir}')

            if builder_move(ct, self.builder_search_dir):
                print('Moved. Done Turn')
                return
            else:
                print('Cant move. Rotating')
                self.builder_search_dir = self.builder_search_dir.rotate_right().rotate_right()

    else:
        print('Moving to target ore')

        # Is target ore still vacant?
        if not ct.is_tile_empty(self.builder_target_ore):
            print('Target ore not vacant anymore. Ending Turn')
            self.builder_target_ore = None
            self.builder_searching = True
            return

        # Is target ore within range?
        distance = builder_pos.distance_squared(self.builder_target_ore)
        if distance <= GameConstants.ACTION_RADIUS_SQ:
            print(f'Distance={distance} <= ActionRadius={
                  GameConstants.ACTION_RADIUS_SQ}')
            # Build harvestor
            if ct.can_build_harvester(self.builder_target_ore):
                ct.build_harvester(self.builder_target_ore)
                self.builder_mine_positions[self.builder_target_ore] = True
                self.builder_target_ore = None
                self.builder_searching = True
        else:
            # Move towards it
            print(f'Not close enough to ore. Distance={
                  distance} > ActionRadius={GameConstants.ACTION_RADIUS_SQ}')
            dir = builder_moveable_dir(ct, builder_pos, self.builder_target_ore)

            if builder_move(ct, dir):
                print('Moved. Done Turn')
                return
            else:
                print('Cant move towards ore... Idk what to do...')
                new_dir = dir.rotate_right().rotate_right()
                builder_move(ct, new_dir)
