import cv2
import numpy as np

from color_utils import color_eq, get_color

y_intercept = 408
color_tolerance = 50

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
        bbox = self._find_bounds(screen, coords)
        dx = bbox[2] - bbox[0]
        dy = bbox[3] - bbox[1]
        return [int(bbox[0] + (dx / 2)), int(bbox[1] + (dy / 2))]

    def _find_bounds(self, screen, coords):
        # TODO fill space and find weighted center
        bbox = [coords[0], coords[1], coords[0], coords[1]]
        for x in range(coords[0], 0, -1):
            c = get_color(screen, [x, coords[1]])
            if color_eq(c, self.color, color_tolerance):
                bbox[0] = x
            else:
                break

        for x in range(coords[0], screen.shape[0], 1):
            c = get_color(screen, [x, coords[1]])
            if color_eq(c, self.color, color_tolerance):
                bbox[2] = x
            else:
                break

        for y in range(coords[1], 0, -1):
            c = get_color(screen, [coords[0], y])
            if color_eq(c, self.color, color_tolerance):
                bbox[1] = y
            else:
                break

        for y in range(coords[1], screen.shape[1], 1):
            c = get_color(screen, [coords[0], y])
            if color_eq(c, self.color, color_tolerance):
                bbox[3] = y
            else:
                break

        return bbox

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
