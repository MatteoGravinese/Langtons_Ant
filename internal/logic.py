class tile:
    def __init__(self, x_pos, y_pos):
        self.pos = (x_pos, y_pos)
        self.color = 0

    def change_color(self):
        if self.color == 0:
            self.color = 1
        elif self.color == 1:
            self.color = 0

class ant:
    dirs = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    def __init__(self, x_origin, y_origin):
        self.pos = [x_origin, y_origin]
        self.facing = 3

    def square_logic(self):
        if tiles[tuple(self.pos)].color == 0:
            self.facing = (self.facing - 1) % 4
        elif tiles[tuple(self.pos)].color == 1:
            self.facing = (self.facing + 1) % 4
        tile.change_color(tiles[tuple(self.pos)])
        return(ant.move(self))

    def move(self):
        dx, dy = ant.dirs[self.facing]
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

x_size = 100
y_size = 100
tiles = {(x, y): tile(x, y) for x in range(x_size) for y in range(y_size)}
langton = ant(x_size // 2, y_size // 2)
tick = 0
safe = True
while tick < 20000 and safe:
    safe = langton.square_logic()
    tick += 1
for y in range(y_size):
    row = []
    for x in range(x_size):
        row.append(tiles[(x, y)].color)
    print(row)