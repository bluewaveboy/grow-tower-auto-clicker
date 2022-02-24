from turtle import position
import numpy as np
from PIL import ImageGrab, Image
import cv2

game_coords = [0, 0, 945, 604]
y_intercept = 408
stop_distance = 30

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
        self.pts = []
        self.initial_coords = initial_coords
        self.color = get_color(screen, initial_coords)
        center = self._find_center(screen, initial_coords)
        self.pts.append(center)
    
    def update(self, screen):
        current_center = self.pts[-1]
        new_coords = self._find_new_coords(screen, current_center)
        new_center = self._find_center(screen, new_coords)
        if current_center[0] != new_center[0] and current_center[1] != new_center[1]:
            self.pts.append(new_center)

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

    def get_line(self):
        pt1 = self.pts[0]
        pt2 = self.pts[-1]
        x1 = pt1[0]
        y1 = pt1[1]
        x2 = pt2[0]
        y2 = pt2[1]
        if y2 - y1 != 0:
            m = (x2 - x1) / (y2 - y1)
            x = (m * (y_intercept - y1)) + x1
            pt2 = [int(x), y_intercept]
        return (pt1, pt2)

    def get_distance(self):
        pt1 = self.pts[0]
        pt2 = self.pts[-1]
        dx = pt2[0] - pt1[0]
        dy = pt2[1] - pt1[1]
        return (dx ** 2 + dy ** 2) ** 0.5

def read_screen():
    return np.array(ImageGrab.grab(bbox=game_coords))

screen = read_screen()
trackers = []
positions = [
    [400, 348],
    [461, 334],
    [519, 361],
    [532, 425],
    [506, 481],
    [441, 495],
    [384, 467],
    [371, 404]
]
colors = [
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (255, 0, 255),
    (0, 255, 255),
    (0, 0, 0),
    (255, 255, 255)
]
for pos in positions:
    tracker = HeadTracker()
    tracker.init(screen, pos)
    trackers.append(tracker)

stop = False
cv2.imshow("Tracking", screen)
while True:
    screen = read_screen()
    for tracker, color in zip(trackers, colors):
        if not stop:
            tracker.update(screen)
        for pt in tracker.pts:
            cv2.circle(screen, pt, 2, color, 3)
        (line_pt1, line_pt2) = tracker.get_line()
        cv2.line(screen, line_pt1, line_pt2, color, 1)
    for tracker in trackers:
        if tracker.get_distance() > stop_distance:
            stop = True
    cv2.imshow("Tracking", screen)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break
