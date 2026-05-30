class Tile:
    def __init__(self, x_pos, y_pos):
        self.pos = (x_pos, y_pos)
        self.color = 0

    def change_color(self):
        self.color = 1 - self.color

class Ant:
    dirs = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    def __init__(self, x_origin=0, y_origin=0):
        self.pos = [x_origin, y_origin]
        self.facing = 3

    def square_logic(self, tiles):
        pos = tuple(self.pos)
        if pos not in tiles:
            tiles[pos] = Tile(*pos)

        if tiles[pos].color == 0:
            self.facing = (self.facing - 1) % 4
        elif tiles[pos].color == 1:
            self.facing = (self.facing + 1) % 4
        tiles[pos].change_color()
        self.move()

    def move(self):
        dx, dy = Ant.dirs[self.facing]
        self.pos[0] += dx
        self.pos[1] += dy
