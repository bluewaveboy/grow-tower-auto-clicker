
import time
import numpy as np
from PIL import ImageGrab
import cv2

from head_tracker import HeadTracker

stop_distance = 30

head_positions = [
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

class HeadTrackers:
    def init(self, screen):
        self.head_trackers = []
        for head_position in head_positions:
            head_tracker = HeadTracker()
            head_tracker.init(screen, head_position)
            self.head_trackers.append(head_tracker)

    def update(self, screen):
        for head_tracker in self.head_trackers:
            if head_tracker.get_distance() < stop_distance:
                head_tracker.update(screen)

    def debug(self, screen):
        for head_tracker, color in zip(self.head_trackers, colors):
            head_tracker.debug(screen, color)

game_coords = [0, 0, 945, 604]

def read_screen():
    return np.array(ImageGrab.grab(bbox=game_coords))

time.sleep(1)
print("3")
time.sleep(1)
print("2")
time.sleep(1)
print("1")
time.sleep(1)
print("go")
start_time = time.time()
screens = []
while time.time() - start_time < 8:
    screen = read_screen()
    screens.append(screen)
print("complete")

head_trackers = HeadTrackers()
head_trackers.init(screens[0])
for screen in screens:
    head_trackers.update(screen)

cv2.imshow("Tracking", screen)
while True:
    screen = read_screen()
    head_trackers.debug(screen)
    cv2.imshow("Tracking", screen)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break
quit()

