import cv2
import numpy as np
from PIL import ImageGrab

from color_utils import color_eq, get_color

y_intercept = 408
color_tolerance = 50
find_center_size = 20

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
        self.pts = []
        self.initial_coords = initial_coords
        self.color = get_color(screen, initial_coords)
        center = self._find_center(screen, initial_coords)
        self.pts.append(center)
    
    def update(self, screen):
        current_center = self.pts[-1]
        new_coords = self._find_new_coords(screen, current_center)
        new_center = self._find_center(screen, new_coords)
        if new_center is None:
            return
        # TODO stop if new center if too far from calculated line
        if abs(current_center[0] - new_center[0]) > 2 or abs(current_center[1] - new_center[1]) > 2:
            self.pts.append(new_center)

    def _find_new_coords(self, screen, starting_pt):
        for pt in spiral(80, 80):
            x = starting_pt[0] + pt[0]
            y = starting_pt[1] + pt[1]
            pt_color = get_color(screen, [x, y])
            if color_eq(pt_color, self.color, color_tolerance):
                return [x, y]
        return starting_pt

    def _find_center(self, screen, coords):
        fill = np.zeros((find_center_size, find_center_size))
        find_center_size_div_2 = int(find_center_size / 2)
        self._fill(
            screen,
            fill,
            [coords[0] - find_center_size_div_2, coords[1] - find_center_size_div_2],
            [find_center_size_div_2, find_center_size_div_2]
        )
        x_sum = 0
        y_sum = 0
        count = 0
        for y in range(0, find_center_size):
            for x in range(0, find_center_size):
                if fill[x, y] == 1:
                    x_sum = x_sum + x
                    y_sum = y_sum + y
                    count = count + 1
        if count == 0:
            return None
        x_avg = int(x_sum / count) + coords[0]
        y_avg = int(y_sum / count) + coords[1]
        return [x_avg, y_avg]

    def _fill(self, screen, fill, screen_coords, coords):
        if fill[coords[0], coords[1]] != 0:
            return

        c = get_color(screen, [screen_coords[0] + coords[0], screen_coords[1] + coords[1]])
        if color_eq(c, self.color, color_tolerance):
            fill[coords[0], coords[1]] = 1
            if coords[0] + 1 < find_center_size:
                self._fill(screen, fill, screen_coords, [coords[0] + 1, coords[1]])    
            if coords[0] - 1 >= 0:
                self._fill(screen, fill, screen_coords, [coords[0] - 1, coords[1]])    
            if coords[1] + 1 < find_center_size:
                self._fill(screen, fill, screen_coords, [coords[0], coords[1] + 1])    
            if coords[1] - 1 >= 0:
                self._fill(screen, fill, screen_coords, [coords[0], coords[1] - 1])    
        else:
            fill[coords[0], coords[1]] = -1

    def get_line(self):
        pt1 = self.pts[0]
        pt2 = self.pts[-1]
        if pt1[0] == pt2[0] and pt1[1] == pt2[1]:
            return None
        
        x_pts = [pt[0] for pt in self.pts]
        y_pts = [pt[1] for pt in self.pts]

        x_pts = np.array(x_pts)
        if abs(np.min(x_pts) - np.max(x_pts)) < 20:
            pt2[1] = y_intercept            
            return (pt1, pt2)
        y_pts = np.array(y_pts)
        model = np.polyfit(x_pts, y_pts, 1)
        m = model[0]
        b = model[1]

        x = int((y_intercept - b) / m)
        pt2 = [x, y_intercept]

        return (pt1, pt2)

    def get_distance(self):
        pt1 = self.pts[0]
        pt2 = self.pts[-1]
        dx = pt2[0] - pt1[0]
        dy = pt2[1] - pt1[1]
        return (dx ** 2 + dy ** 2) ** 0.5

    def debug(self, screen, color):
        for pt in self.pts:
            cv2.circle(screen, pt, 2, color, 3)
        line = self.get_line()
        if line is not None:
            (line_pt1, line_pt2) = line
            cv2.line(screen, line_pt1, line_pt2, color, 1)

# game_coords = [0, 0, 945, 604]

# def read_screen():
#     return np.array(ImageGrab.grab(bbox=game_coords))

# coords = [400, 348]
# screen = read_screen()
# t = HeadTracker()
# t.init(screen, coords)
# center = t._find_center(screen, coords)
# print(center)