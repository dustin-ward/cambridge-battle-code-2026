
class NaivePathfinder():
    def __init__(self, R, C, card=False):
        self.R = R
        self.C = C
        self.card = card

    def search(self, grid, src, dst):
        path = []

        x, y = src
        while (x, y) != dst:
            dx = 0
            dy = 0
            if dst[0] > x:
                dx += 1
            elif dst[0] < x:
                dx -= 1
            if dst[1] > y:
                dy += 1
            elif dst[1] < y:
                dy -= 1
            x += dx
            y += dy
            path.append((y, x))

        return path

