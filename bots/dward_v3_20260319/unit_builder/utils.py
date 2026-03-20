from enum import Enum
from cambc import Direction, Environment, GameConstants, Position

DIRECTIONS = [d for d in Direction if d != Direction.CENTRE]
CARD_DIRECTIONS = [Direction.NORTH, Direction.EAST,
                   Direction.SOUTH, Direction.WEST]
ORES = [Environment.ORE_TITANIUM, Environment.ORE_AXIONITE]


class State(Enum):
    EXPLORING = 0
    BUILDING_DEFENCE = 1
    BUILDING_MINE = 2


def scan_surroundings(self):
    """
    Look at every tile in vision radius and note its type and the unit on it
    """
    for pos in self.c.get_nearby_tiles():
        (x, y) = pos
        if self.map_mem[y][x] is None:
            self.map_mem[y][x] = {}

            if on_vision_boundary(self, pos):
                self.bldr_vsn_bndry.add(pos)

        if not on_vision_boundary(self, pos) and pos in self.bldr_vsn_bndry:
            self.bldr_vsn_bndry.remove(pos)

        env = self.c.get_tile_env((x, y))
        self.map_mem[y][x]['Environment'] = env

        building_id = self.c.get_tile_building_id((x, y))
        self.map_mem[y][x]['building_id'] = building_id

        if building_id is not None:
            self.map_mem[y][x]['EntityType'] = self.c.get_entity_type(
                building_id)
            self.map_mem[y][x]['Team'] = self.c.get_team(building_id)


def builder_move(self, pos: Position, build_conveyor=False) -> bool:
    """Try to move to pos. Return T/F if success/fail"""
    dir = self.c.get_position().direction_to(pos)
    print(f'builder_move({pos},conv={build_conveyor}) -> {dir}')

    distance = self.c.get_position().distance_squared(pos)
    assert distance <= GameConstants.ACTION_RADIUS_SQ, f'pos({pos}) not within moveable range!'

    scan_surroundings(self)

    if build_conveyor:
        assert distance < GameConstants.ACTION_RADIUS_SQ, 'tried to build conveyor and move on diagonal!'
        if self.c.can_build_conveyor(pos, dir.opposite()):
            self.c.build_conveyor(pos, dir.opposite())
        else:
            print(f'couldn\'t build conveyor at {pos} dir={dir.opposite()}')
    else:
        if self.c.can_build_road(pos):
            self.c.build_road(pos)
        else:
            print(f'couldn\'t build road at {pos}')

    if self.c.can_move(dir):
        self.c.move(dir)
        return True
    return False


def bounds(self, x, y):
    return x >= 0 and x < self.map_width and y >= 0 and y < self.map_height


def on_vision_boundary(self, pos):
    x, y = self.c.get_position()
    x2, y2 = pos

    dx = abs(x - x2)
    dy = abs(y - y2)

    if dx == 4 or dy == 4:
        return True
    elif dx == 3 and dy == 3:
        return True
    else:
        return False

