import numpy as np
from PIL import ImageGrab, Image

game_coords = [0, 0, 1460, 840]

def get_color(screen, coords):
    return screen[coords[1], coords[0]]

def color_eq(c1, c2):
    diff = 0
    for i in range(0, 3):
        p1 = int(c1[i])
        p2 = int(c2[i])
        diff = diff + abs(p1 - p2)
    return diff < 50


def spiral(width, height):
    x = y = 0
    dx = 0
    dy = -1
    for i in range(max(width, height) ** 2):
        if (-width / 2 < x <= width / 2) and (-height / 2 < y <= height / 2):
            yield [x, y]
        if x == y or (x < 0 and x == -y) or (x > 0 and x == 1 - y):
            dx, dy = -dy, dx
        x, y = x+dx, y+dy
        
class HeadTracker:
    def init(self, screen, initial_coords):
        self.initial_coords = initial_coords
        self.color = get_color(screen, initial_coords)
        self.current_center = self.initial_center = self._find_center(screen, initial_coords)
        print(self.initial_center)
    
    def update(self, screen):
        new_coords = self._find_new_coords(screen, self.current_center)
        self.current_center = self._find_center(screen, new_coords)
        print(self.current_center)

    def _find_new_coords(self, screen, starting_pt):
        for pt in spiral(40, 40):
            x = starting_pt[0] + pt[0]
            y = starting_pt[1] + pt[1]
            pt_color = get_color(screen, [x, y])
            if color_eq(pt_color, self.color):
                return [x, y]
        return starting_pt

    def _find_center(self, screen, coords):
        bbox = self._find_bounds(screen, coords)
        dx = bbox[2] - bbox[0]
        dy = bbox[3] - bbox[1]
        return [int(bbox[0] + (dx / 2)), int(bbox[1] + (dy / 2))]

    def _find_bounds(self, screen, coords):
        bbox = [coords[0], coords[1], coords[0], coords[1]]
        for x in range(coords[0], 0, -1):
            c = get_color(screen, [x, coords[1]])
            if color_eq(c, self.color):
                bbox[0] = x
            else:
                break

        for x in range(coords[0], screen.shape[0], 1):
            c = get_color(screen, [x, coords[1]])
            if color_eq(c, self.color):
                bbox[2] = x
            else:
                break

        for y in range(coords[1], 0, -1):
            c = get_color(screen, [coords[0], y])
            if color_eq(c, self.color):
                bbox[1] = y
            else:
                break

        for y in range(coords[1], screen.shape[1], 1):
            c = get_color(screen, [coords[0], y])
            if color_eq(c, self.color):
                bbox[3] = y
            else:
                break

        return bbox

def read_screen():
    return np.array(ImageGrab.grab(bbox=game_coords))

screen = read_screen()
tracker = HeadTracker()
tracker.init(screen, [400, 348])

while True:
    screen = read_screen()
    tracker.update(screen)
