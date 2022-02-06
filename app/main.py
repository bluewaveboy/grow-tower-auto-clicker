import numpy as np
from PIL import ImageGrab, Image
import cv2
from directKeys import click, move_mouse_to, query_mouse_position, press_key, release_key, query_key_state, move_window, KEY_Q, KEY_CONTROL
import time
import math

upgrade_castle = True
upgrade_archers = True
upgrade_tower_weapons = False

game_coords = [0, 0, 1460, 840]
debug_tracking = False

screen = None

def read_screen():
    global screen
    screen = np.array(ImageGrab.grab(bbox=game_coords))
    # screen = np.array(Image.open('C:/dev/grow-tower-auto-clicker-files/where-is-the-diamond-02.png'))
    return screen

def get_color(x, y):
    return screen[game_coords[1] + y, game_coords[0] + x]

def check_color(x, y, color):
    return np.array_equal(get_color(x, y), color)

def check_color_around(x, y, radius, color):
    for ix in range(x - radius, x + radius):
        for iy in range(y - radius, y + radius):
            if check_color(ix, iy, color):
                return True
    return False

def solve_where_is_the_diamond():
    global screen
    y_intercept = 524
    head_locations_x = [347, 445, 540, 637, 735, 830, 928, 1026]
    read_screen()
    tracker = cv2.TrackerCSRT_create()

    head_width = 36
    head_height = 44

    # top
    if check_color_around(678, 342, 35, [67, 196, 255]):
        head_x = game_coords[0] + 651
        head_y = game_coords[0] + 384

    # top/right
    elif check_color_around(837, 389, 35, [67, 196, 255]):
        head_x = game_coords[0] + 747
        head_y = game_coords[0] + 418

    # right
    elif check_color_around(862, 541, 35, [67, 196, 255]):
        head_x = game_coords[0] + 782
        head_y = game_coords[0] + 517

    # bottom/right
    elif check_color_around(837, 680, 35, [67, 196, 255]):
        head_x = game_coords[0] + 747
        head_y = game_coords[0] + 613

    # bottom
    elif check_color_around(678, 730, 35, [67, 196, 255]):
        head_x = game_coords[0] + 651
        head_y = game_coords[0] + 648

    # bottom/left
    elif check_color_around(528, 680, 35, [67, 196, 255]):
        head_x = game_coords[0] + 550
        head_y = game_coords[0] + 613

    # left
    elif check_color_around(491, 541, 35, [67, 196, 255]):
        head_x = game_coords[0] + 526
        head_y = game_coords[0] + 517

    # top/left
    elif check_color_around(528, 389, 35, [67, 196, 255]):
        head_x = game_coords[0] + 550
        head_y = game_coords[0] + 418

    else:
        print(get_color(678, 342))
        print("could not determine diamond location")
        quit()

    # initialize the object tracker to track the head
    tracker.init(screen, (head_x, head_y, head_width, head_height))
    
    # track the head
    if debug_tracking:
        cv2.imshow("Tracking", screen)
    target_x = None
    target_y = None
    last_bbox = None
    found_time = None
    while True:
        read_screen()
        ok, bbox = tracker.update(screen)
        if not ok:
            print("lost tracking")
            while True:
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        
        bbox_x = bbox[0]
        bbox_y = bbox[1]
        bbox_w = bbox[2]
        bbox_h = bbox[3]
        
        # draw bounding box
        if debug_tracking:
            cv2.rectangle(screen, (int(bbox_x), int(bbox_y)), (int(bbox_x + bbox_w), int(bbox_y + bbox_h)), (0, 255, 0), 2, 1)
        if target_x is None:
            has_moved_x = abs(bbox_x - head_x) > 10
            has_moved_y = abs(bbox_y - head_y) > 10
            if has_moved_x or has_moved_y:
                # use the center of the tracking box
                x1 = head_x + (head_width / 2)
                y1 = head_y + (head_height / 2)
                x2 = bbox_x + (bbox_w / 2)
                y2 = bbox_y + (bbox_h / 2)
                m = (y2 - y1) / (x2 - x1)
                b = y1 - (m * x1)
                x = (y_intercept - b) / m
                target_x = x
                target_y = y_intercept
                last_bbox = bbox
                found_time = time.time()

        if debug_tracking:
            if target_x is not None:
                cv2.rectangle(screen, (int(head_x), int(head_y)), (int(head_x + head_width), int(head_y + head_height)), (0, 255, 0), 2, 1)
                cv2.rectangle(screen, (int(last_bbox[0]), int(last_bbox[1])), (int(last_bbox[0] + last_bbox[2]), int(last_bbox[1] + last_bbox[3])), (0, 255, 0), 2, 1)
                cv2.line(screen, (int(head_x + (head_width / 2)), int(head_y + (head_height / 2))), (int(target_x), int(target_y)), (0, 255, 0))
            cv2.imshow("Tracking", screen)    
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break
        
        # wait a bit then click the head
        if found_time is not None and time.time() - found_time > 4:
            closest_head_x = target_x
            closest_head_distance = 99999
            for x in head_locations_x:
                distance_to_target = abs(target_x - x)
                if distance_to_target < closest_head_distance:
                    closest_head_distance = distance_to_target
                    closest_head_x = x
            
            move_mouse_to(closest_head_x, target_y)
            click(closest_head_x, target_y)
            time.sleep(2)
            break
            

# only start the program after the mouse is in the top left corner
print("move the mouse to the upper left corner to start")
while True:
    mouse_pos = query_mouse_position()
    if mouse_pos.x <= 0 and mouse_pos.y <= 0:
        break

print("here we go")
move_window(u'Qt5154QWindowOwnDCIcon', None, 0, 0, 1453, 832)
while not query_key_state(KEY_CONTROL):
    print("checking (hold CTRL to exit)")
    read_screen()
    
    # dismiss "Daily Event"
    if check_color(1100, 153, [35, 33, 30]):
        print("dismiss 'Daily Event'")
        click(1100, 153)
        time.sleep(1)

    # click "Battle"
    if check_color(1318, 771, [191, 185, 172]):
        # upgrade castle
        if upgrade_castle and check_color(1056, 193, [56, 142, 211]):
            print("upgrading castle")
            click(1056, 193)
            time.sleep(1)

        # upgrade archers        
        if upgrade_archers and check_color(1056, 303, [54, 136, 203]):
            print("upgrading archers")
            click(1056, 303)
            time.sleep(1)
            
        # upgrade tower weapons
        if upgrade_tower_weapons:
            print("upgrading tower weapon")
            
            # switch to towers
            click(419, 540)
            time.sleep(1)
            # click tower to upgrade
            click(420, 335)
            time.sleep(1)
            
            # click upgrade (spend gems)
            click(994, 560)
            time.sleep(1)
            click(994, 560)
            time.sleep(1)
            click(994, 560)
            time.sleep(1)
            # click x on upgrade
            click(1104, 207)
            time.sleep(1)
            click(1357, 116)
            time.sleep(1)
        
        print("click 'Battle'")
        click(1318, 771)
        time.sleep(1)
        
    # click "2x"
    if check_color(78, 759, [0, 0, 0]):
        print("click '2x'")
        click(78, 759)
        time.sleep(1)
    
    # where is the diamond?
    if check_color(354, 713, [167, 118, 59]) and check_color(415, 121, [167, 167, 167]) and check_color(934, 222, [223, 223, 223]):
        # don't click start if we have a timer "time left"
        if not check_color(416, 618, [219, 219, 219]):
            click(348, 751)
            solve_where_is_the_diamond()
    
    # get the color of a pixel
    # print(get_color(934, 222))

    time.sleep(1)
    move_mouse_to(100, 100)
    time.sleep(1)
    move_mouse_to(200, 200)

print("done")
