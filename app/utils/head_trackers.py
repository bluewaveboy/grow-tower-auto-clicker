
import datetime
from pathlib import Path
import time
import numpy as np
from PIL import ImageGrab, Image
import cv2

from utils.head_tracker import HeadTracker

stop_distance = 30

head_positions = [
    [689, 417],
    [777, 463],
    [795, 555],
    [758, 642],
    [658, 661],
    [575, 621],
    [555, 525],
    [597, 441]
]

end_head_x_positions = [347, 445, 540, 637, 735, 830, 928, 1026]

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

    def complete(self):
        final_head_positions = [-1, -1, -1, -1, -1, -1, -1, -1]
        for i in range(0, 8):
            min_head, min_dest_pos = self._get_best_match(final_head_positions)
            final_head_positions[min_head] = min_dest_pos
        self.final_head_positions = final_head_positions

    def _get_best_match(self, final_head_positions):
        min_distance = 1000000
        min_head = -1
        min_dest_pos = -1
        for head in range(0, 8):
            if final_head_positions[head] == -1:
                d, dest_pos = self._find_best_distance(head, final_head_positions)
                if d < min_distance:
                    min_distance = d
                    min_head = head
                    min_dest_pos = dest_pos
        return min_head, min_dest_pos

    def _find_best_distance(self, head, final_head_positions):
        min_distance = 1000000
        min_final_pos = 0
        line = self.head_trackers[head].get_line()
        x = line[1][0]
        for dest_pos in range(0, 8):
            if self._is_position_taken(dest_pos, final_head_positions):
                continue
            if dest_pos == 0 and x < end_head_x_positions[0]:
                d = 0
            elif dest_pos == 7 and x > end_head_x_positions[-1]:
                d = 0
            else:
                d = abs(x - end_head_x_positions[dest_pos])
            if d < min_distance:
                min_distance = d
                min_final_pos = dest_pos

        return min_distance, min_final_pos

    def _is_position_taken(self, dest_pos, final_head_positions):
        for hp in final_head_positions:
            if hp == dest_pos:
                return True
        return False

    def debug(self, screen):
        for head_tracker, color in zip(self.head_trackers, colors):
            head_tracker.debug(screen, color)

# game_coords = [0, 0, 945, 604]

# p = Path("screenshots") / "2022-02-27_16_53_51.590434"
# paths = [str(p) for p in p.iterdir() if str(p).endswith('.png')]
# paths.sort()
# screens = []
# print(f"reading {len(paths)} screens")
# for f in paths:
#     img = Image.open(f)
#     screens.append(np.array(img))

# print("calculating")
# head_trackers = HeadTrackers()
# head_trackers.init(screens[0])
# for screen in screens:
#     head_trackers.update(screen)
# head_trackers.complete()
# print("final_head_positions", head_trackers.final_head_positions)

# cv2.imshow("Tracking", screen)
# while True:
#     screen = np.array(ImageGrab.grab(bbox=game_coords))
#     head_trackers.debug(screen)
#     cv2.imshow("Tracking", screen)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         cv2.destroyAllWindows()
#         break
# quit()

