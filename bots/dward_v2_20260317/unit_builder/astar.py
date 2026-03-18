import heapq

from cambc import Direction, Environment, EntityType


class Cell:
    def __init__(self):
        self.parent_i = 0  # Parent cell's row index
        self.parent_j = 0  # Parent cell's column index
        self.f = float('inf')  # Total cost of the cell (g + h)
        self.g = float('inf')  # Cost from start to this cell
        self.h = 0  # Heuristic cost from this cell to destination


DIST_DIAG = 2**0.5
DIRECTION_D = [d.delta() for d in Direction if d !=
               Direction.CENTRE]  # (dx,dy)
DIRECTION_D_CARD = [d.delta() for d in [Direction.NORTH,
                                        Direction.EAST, Direction.SOUTH, Direction.WEST]]
NON_BLOCKING_ENTITIES = [EntityType.CONVEYOR, EntityType.ROAD]


class AStar:
    def __init__(self, R, C, card=False):
        self.R = R
        self.C = C
        self.card = card

        self.closed_list = [[False for _ in range(C)] for _ in range(R)]
        self.cell_details = [[Cell() for _ in range(C)] for _ in range(R)]

    # Check if a cell is valid (within the grid)
    def bounds(self, row, col):
        return (row >= 0) and (row < self.R) and (col >= 0) and (col < self.C)

    def valid_pos(self, grid, i, j):
        tile = grid[i][j]
        if tile is None:
            print(f'{(i, j)} -> Valid')
            return True

        if tile['Environment'] == Environment.WALL:
            return False

        if tile.get('building_id', None) is None:
            print(f'{(i, j)} -> Valid')
            return True
        else:
            if tile['EntityType'] in NON_BLOCKING_ENTITIES:
                return True
            return False

    # Calculate the heuristic value of a cell (diagonal distance)
    def calculate_h_value(self, row, col, dst):
        dx = abs(col - dst[0])
        dy = abs(row - dst[1])
        return (dx+dy) + (DIST_DIAG - 2) * min(dx, dy)

    # Trace the path from source to destination
    def trace_path(self, cell_details, dst):
        path = []
        row = dst[1]
        col = dst[0]

        # Trace the path from destination to source using parent cells
        while not (self.cell_details[row][col].parent_i == row and self.cell_details[row][col].parent_j == col):
            path.append((row, col))
            temp_row = cell_details[row][col].parent_i
            temp_col = cell_details[row][col].parent_j
            row = temp_row
            col = temp_col

        # Reverse the path to get the path from source to destination
        path.reverse()

        return path

    def search(self, grid, src, dst):
        i = src[1]
        j = src[0]
        self.cell_details[i][j].f = 0
        self.cell_details[i][j].g = 0
        self.cell_details[i][j].h = 0
        self.cell_details[i][j].parent_i = i
        self.cell_details[i][j].parent_j = j

        # Initialize the open list (cells to be visited) with the start cell
        open_list = []
        heapq.heappush(open_list, (0.0, i, j))

        # Initialize the flag for whether destination is found
        found_dest = False

        # Main loop of A* search algorithm
        while len(open_list) > 0:
            # Pop the cell with the smallest f value from the open list
            p = heapq.heappop(open_list)

            # Mark the cell as visited
            i = p[1]
            j = p[2]
            self.closed_list[i][j] = True

            # For each direction, check the successors
            directions = DIRECTION_D_CARD if self.card else DIRECTION_D
            for (dx, dy) in directions:
                ii = i + dy
                jj = j + dx

                # If the successor is valid, unblocked, and not visited
                if self.bounds(ii, jj) and self.valid_pos(grid, i, j) and not self.closed_list[ii][jj]:
                    # If the successor is the destination
                    if (jj, ii) == dst:
                        # Set the parent of the destination cell
                        self.cell_details[ii][jj].parent_i = i
                        self.cell_details[ii][jj].parent_j = j
                        # Trace and print the path from source to destination
                        return self.trace_path(self.cell_details, dst)
                    else:
                        # Calculate the new f, g, and h values
                        g_new = self.cell_details[i][j].g + 1.0
                        h_new = self.calculate_h_value(ii, jj, dst)
                        f_new = g_new + h_new

                        # If the cell is not in the open list or the new f value is smaller
                        if self.cell_details[ii][jj].f == float('inf') or self.cell_details[ii][jj].f > f_new:
                            # Add the cell to the open list
                            heapq.heappush(open_list, (f_new, ii, jj))
                            # Update the cell details
                            self.cell_details[ii][jj].f = f_new
                            self.cell_details[ii][jj].g = g_new
                            self.cell_details[ii][jj].h = h_new
                            self.cell_details[ii][jj].parent_i = i
                            self.cell_details[ii][jj].parent_j = j

        # If the destination is not found after visiting all cells
        if not found_dest:
            return []
