from enum import Enum
from cambc import Direction, Environment, GameConstants, Position, EntityType

DIRECTIONS = [d for d in Direction if d != Direction.CENTRE]
CARD_DIRECTIONS = [Direction.NORTH, Direction.EAST,
                   Direction.SOUTH, Direction.WEST]
ORES = [Environment.ORE_TITANIUM, Environment.ORE_AXIONITE]

SPLITTER_DT = [
    (-1, -2, Direction.SOUTH),
    (2, -1, Direction.WEST),
    (1, 2, Direction.NORTH),
    (-2, -1, Direction.EAST),
    (1, -2, Direction.SOUTH),
    (2, 1, Direction.WEST),
    (-1, 2, Direction.NORTH),
    (-2, 1, Direction.EAST),
]


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
        import sys
        if y >= len(self.map_mem) or x >= len(self.map_mem[0]):
            print(f'x = {x} y = {y}', file=sys.stderr)
            print(f'map_height={self.map_height} map_width={self.map_width}', file=sys.stderr)
            print(f'len(map_mem)={len(self.map_mem)} len(map_mem[0])={len(self.map_mem[0])}', file=sys.stderr)
        if bounds(self, x, y) and self.map_mem[y][x] is None:
            self.map_mem[y][x] = {}

            if on_vision_boundary(self, pos):
                self.vsn_bndry.add(pos)

        if not on_vision_boundary(self, pos) and pos in self.vsn_bndry:
            self.vsn_bndry.remove(pos)

        env = self.c.get_tile_env((x, y))
        self.map_mem[y][x]['Environment'] = env

        building_id = self.c.get_tile_building_id((x, y))
        self.map_mem[y][x]['building_id'] = building_id

        if building_id is not None:
            self.map_mem[y][x]['EntityType'] = self.c.get_entity_type(
                building_id)
            self.map_mem[y][x]['Team'] = self.c.get_team(building_id)


def builder_move(self, pos: Position, build_conveyor=False, scan=True) -> bool:
    """Try to move to pos. Return T/F if success/fail"""
    dir = self.c.get_position().direction_to(pos)
    print(f'builder_move({pos},conv={build_conveyor}) -> {dir}')

    distance = self.c.get_position().distance_squared(pos)
    assert distance <= GameConstants.ACTION_RADIUS_SQ, f'pos({pos}) not within moveable range!'

    if scan:
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


def is_core(self, pos: Position) -> bool:
    core_id = self.c.get_tile_building_id(pos)
    return core_id is not None and self.c.get_entity_type(core_id) == EntityType.CORE


def get_center_of_core(self, start_pos: Position) -> Position:
    """Get center of core given any other tile that the core also occupies"""

    assert is_core(self, start_pos), (
        f'called `get_center_of_core()` on non-core tile: {start_pos}'
    )

    # BFS search for center of core
    Q = [start_pos]
    V = set(Q)
    while Q:
        cur = Q[0]
        Q = Q[1:]
        core_count = 0

        x, y = cur
        for d in CARD_DIRECTIONS:
            dx, dy = d.delta()
            xx = x + dx
            yy = y + dy
            pos2 = Position(xx, yy)

            if bounds(self, xx, yy) and is_core(self, pos2):
                core_count += 1
                if pos2 not in V:
                    Q.append(pos2)
                    V.add(pos2)

        if core_count == 4:
            return cur

    raise AssertionError(f'couldn\'t find center of core starting at {start_pos}')


def yx_to_pos(coords: tuple) -> Position:
    return Position(coords[1], coords[0])


def can_afford(self, base_cost: tuple[int, int]) -> bool:
    ti, ax = self.c.get_global_resources()
    have_ti = base_cost[0] * (self.c.get_scale_percent() / 100) <= ti
    have_ax = base_cost[1] * (self.c.get_scale_percent() / 100) <= ax
    return have_ti and have_ax


def is_road(self, pos: Position):
    building_id = self.c.get_tile_building_id(pos)
    return building_id is not None and self.c.get_entity_type(building_id) == EntityType.ROAD


def is_conveyor(self, pos: Position):
    building_id = self.c.get_tile_building_id(pos)
    return building_id is not None and self.c.get_entity_type(building_id) == EntityType.CONVEYOR


def is_splitter(self, pos: Position):
    building_id = self.c.get_tile_building_id(pos)
    return building_id is not None and self.c.get_entity_type(building_id) == EntityType.SPLITTER


def is_sentinel(self, pos: Position):
    building_id = self.c.get_tile_building_id(pos)
    return building_id is not None and self.c.get_entity_type(building_id) == EntityType.SENTINEL


def is_foundry(self, pos: Position):
    building_id = self.c.get_tile_building_id(pos)
    return building_id is not None and self.c.get_entity_type(building_id) == EntityType.FOUNDRY


def get_splitter_locations(self) -> list[tuple[Position, Direction]]:
    ret = []
    for dx, dy, dir in SPLITTER_DT:
        x, y = self.core_pos
        x += dx
        y += dy
        if bounds(self, x, y):
            ret.append((yx_to_pos((y, x)), dir))
    return ret
