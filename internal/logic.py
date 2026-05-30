class Tile:
    def __init__(self, x_pos, y_pos, color=0):
        self.pos = (x_pos, y_pos)
        self.color = color

class Ant:
    dirs = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    turn_values = {
        'left': -1,
        'right': 1,
        'back': 2
    }

    def __init__(self, x_origin=0, y_origin=0):
        self.pos = [x_origin, y_origin]
        self.facing = 3

    def square_logic(self, tiles, rules):
        pos = tuple(self.pos)
        if pos not in tiles:
            tiles[pos] = Tile(*pos)
        rule = rules[tiles[pos].color]
        self.facing = (self.facing + Ant.turn_values[rule['turn']]) % 4
        tiles[pos].color = rule['next_color']
        self.move()

    def move(self):
        dx, dy = Ant.dirs[self.facing]
        self.pos[0] += dx
        self.pos[1] += dy
