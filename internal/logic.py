class Tile:
    def __init__(self, x_pos, y_pos):
        self.pos = (x_pos, y_pos)
        self.color = 0

    def change_color(self):
        if self.color == 0:
            self.color = 1
        elif self.color == 1:
            self.color = 0

class Ant:
    dirs = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    def __init__(self, x_origin, y_origin):
        self.pos = [x_origin, y_origin]
        self.facing = 3

    def square_logic(self, tiles, x_size, y_size):
        if tiles[tuple(self.pos)].color == 0:
            self.facing = (self.facing - 1) % 4
        elif tiles[tuple(self.pos)].color == 1:
            self.facing = (self.facing + 1) % 4
        tiles[tuple(self.pos)].change_color()
        return(self.move(x_size, y_size))

    def move(self, x_size, y_size):
        dx, dy = Ant.dirs[self.facing]
        self.pos[0] += dx
        self.pos[1] += dy
        if self.pos[0] == 0:
            return False
        if self.pos[0] == x_size:
            return False
        if self.pos[1] == 0:
            return False
        if self.pos[1] == y_size:
            return False
        return True