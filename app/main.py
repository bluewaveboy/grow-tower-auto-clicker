import datetime
from pathlib import Path
from utils.head_trackers import HeadTrackers, end_head_x_positions
from utils.head_tracker import y_intercept
import numpy as np
from PIL import ImageGrab
from utils.direct_keys import click, move_mouse_to, query_mouse_position, press_key, release_key, query_key_state, move_window, KEY_Q, KEY_CONTROL
import time

upgrade_castle = True
upgrade_archers = True
upgrade_heros = True
upgrade_tower_weapons = True
upgrade_leader = True

# game_coords = [0, 0, 1460, 840]
game_coords = [3, 74, 1470, 911]
hero_locations = [
    [332, 139],
    [416, 139],
    [504, 139],
    [332, 241],
    [416, 241],
    [504, 241],
    [332, 347],
    [416, 347],
    [504, 347],
    [332, 441],
    [416, 441],
    [504, 441]
]
tower_weapon_locations = [
    [422, 229],
    [422, 332],
    [422, 442]
]
debug_tracking = True

screen = None

def read_screen():
    global screen
    screen = np.array(ImageGrab.grab(bbox=game_coords))
    # screen = np.array(Image.open('C:/dev/grow-tower-auto-clicker-files/where-is-the-diamond-02.png'))
    return screen

def get_color(x, y):
    return screen[y, x]

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
    head_y_click_location = 524
    head_x_click_locations = [347, 445, 540, 637, 735, 830, 928, 1026]
    head_locations = [
        [651, 384],
        [747, 418],
        [782, 517],
        [747, 613],
        [651, 648],
        [550, 613],
        [526, 517],
        [550, 418]
    ]
    colors = [
        (0, 255, 0),
        (0, 0, 255),
        (255, 0, 0),
        (255, 255, 0),
        (255, 0, 255),
        (0, 255, 255),
        (255, 255, 255),
        (0, 0, 0)
    ]

    head_width = 36
    head_height = 44

    # top
    if check_color_around(678, 342, 35, [67, 196, 255]):
        print("diamond is on the top")
        head_x = head_locations[0][0]
        head_y = head_locations[0][1]

    # top/right
    elif check_color_around(837, 389, 35, [67, 196, 255]):
        print("diamond is on the top/right")
        head_x = head_locations[1][0]
        head_y = head_locations[1][1]

    # right
    elif check_color_around(862, 541, 35, [67, 196, 255]):
        print("diamond is on the right")
        head_x = head_locations[2][0]
        head_y = head_locations[2][1]

    # bottom/right
    elif check_color_around(837, 680, 35, [67, 196, 255]):
        print("diamond is on the bottom/right")
        head_x = head_locations[3][0]
        head_y = head_locations[3][1]

    # bottom
    elif check_color_around(678, 730, 35, [67, 196, 255]):
        print("diamond is on the bottom")
        head_x = head_locations[4][0]
        head_y = head_locations[4][1]

    # bottom/left
    elif check_color_around(528, 680, 35, [67, 196, 255]):
        print("diamond is on the bottom/left")
        head_x = head_locations[5][0]
        head_y = head_locations[5][1]

    # left
    elif check_color_around(491, 541, 35, [67, 196, 255]):
        print("diamond is on the left")
        head_x = head_locations[6][0]
        head_y = head_locations[6][1]

    # top/left
    elif check_color_around(528, 389, 35, [67, 196, 255]):
        print("diamond is on the top/left")
        head_x = head_locations[7][0]
        head_y = head_locations[7][1]

    else:
        print("could not determine diamond location")
        quit()
        
    # click start
    click(348, 751)

    # capture all the frames    
    capture_start_time = time.time()
    screens = []
    while time.time() - capture_start_time < 5:
        frame_start_time = time.time()
        screen = ImageGrab.grab(bbox=game_coords)
        screens.append(screen)
        while time.time() - frame_start_time < (1 / 30):
            time.sleep(0.001)

    # initialize the object tracker to track the head
    read_screen()
    head_trackers = []
    head_bboxs = []
    target_x = []
    last_bboxs = []
    for head_location in head_locations:
        head_tracker = cv2.TrackerCSRT_create()
        head_tracker.init(screen, (head_location[0], head_location[1], head_width, head_height))
        head_trackers.append(head_tracker)
        head_bboxs.append([])
        last_bboxs.append(None)
        target_x.append(None)
        
    # track the head
    if debug_tracking:
        cv2.imshow("Tracking", screen)
    while True:
        read_screen()
        for i, head_tracker in enumerate(head_trackers):
            ok, bbox = head_tracker.update(screen)
            if ok:
                head_bboxs[i] = bbox
                bbox_x = bbox[0]
                bbox_y = bbox[1]
                bbox_w = bbox[2]
                bbox_h = bbox[3]

                # use the center of the tracking box
                x1 = head_locations[i][0] + (head_width / 2)
                y1 = head_locations[i][1] + (head_height / 2)
                x2 = bbox_x + (bbox_w / 2)
                y2 = bbox_y + (bbox_h / 2)
                if x2 - x1 != 0:
                    m = (y2 - y1) / (x2 - x1)
                    if m != 0:
                        b = y1 - (m * x1)
                        x = (head_y_click_location - b) / m
                        target_x[i] = x
                        last_bboxs[i] = bbox

                # draw bounding box
                if debug_tracking:
                    cv2.rectangle(screen, (int(bbox_x), int(bbox_y)), (int(bbox_x + bbox_w), int(bbox_y + bbox_h)), colors[i], 2, 1)
                    if target_x[i] is not None:
                        cv2.line(screen, (int(head_locations[i][0] + (head_width / 2)), int(head_locations[i][1] + (head_height / 2))), (int(target_x[i]), int(head_y_click_location)), colors[i])
            
                # if target_x[i] is None:
                #     has_moved_x = abs(bbox_x - head_x) > 10
                #     has_moved_y = abs(bbox_y - head_y) > 10
                #     if has_moved_x or has_moved_y:

        if debug_tracking:
            # if target_x is not None:
            #     cv2.rectangle(screen, (int(head_x), int(head_y)), (int(head_x + head_width), int(head_y + head_height)), (0, 255, 0), 2, 1)
            #     cv2.rectangle(screen, (int(last_bbox[0]), int(last_bbox[1])), (int(last_bbox[0] + last_bbox[2]), int(last_bbox[1] + last_bbox[3])), (0, 255, 0), 2, 1)
            #     
            cv2.imshow("Tracking", screen)    
            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break
        
        # wait a bit then click the head
        # print(f"head is moving to {target_x}")
        # if found_time is not None and time.time() - found_time > 4:
        #     closest_head_i = 0
        #     closest_head_x = target_x
        #     closest_head_distance = 99999
        #     for i, x in enumerate(head_x_click_locations):
        #         distance_to_target = abs(target_x - x)
        #         print(f"trying head {i} as x {x}, distance {distance_to_target} (target_x: {target_x})")
        #         if distance_to_target < closest_head_distance:
        #             closest_head_distance = distance_to_target
        #             closest_head_i = i
        #             closest_head_x = x
            
        #     print(f"target location is {closest_head_i} (x:{closest_head_x})")
        #     move_mouse_to(closest_head_x, target_y)
        #     click(closest_head_x, target_y)
        #     time.sleep(2)
        #     break
            

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
        # upgrade leader
        if upgrade_leader:
            print("upgrading leader")
            # click leader
            click(611, 550)
            time.sleep(1)
            # click upgrade
            click(994, 560)
            time.sleep(0.2)
            click(994, 560)
            time.sleep(0.2)
            click(994, 560)
            time.sleep(0.2)
            # click x on upgrade
            click(1104, 207)
            time.sleep(0.2)
            # click x on heros
            click(1357, 116)
            time.sleep(0.2)
            
        # upgrade castle (if button is active)
        if upgrade_castle and check_color(1056, 193, [56, 142, 211]):
            print("upgrading castle")
            click(1056, 193)
            time.sleep(1)

        # upgrade archer (if button is active)
        if upgrade_archers and check_color(1056, 303, [54, 136, 203]):
            print("upgrading archers")
            click(1056, 303)
            time.sleep(1)
            
        # upgrade heros
        if upgrade_heros:
            for pos in hero_locations:
                print("upgrading hero", pos)
                # click tower
                click(pos[0], pos[1])
                time.sleep(0.2)
                # click upgrade
                click(994, 560)
                time.sleep(0.2)
                click(994, 560)
                time.sleep(0.2)
                click(994, 560)
                time.sleep(0.2)
                # click x on upgrade
                click(1104, 207)
                time.sleep(0.2)
                # click x on heros
                click(1357, 116)
                time.sleep(0.2)
                
            
        # upgrade tower weapons
        if upgrade_tower_weapons:
            print("upgrading tower weapon")
            
            # switch to towers
            click(419, 540)
            time.sleep(3)
            
            for pos in tower_weapon_locations:
                # click tower to upgrade
                click(pos[0], pos[1])
                time.sleep(0.2)

                # click upgrade (spend gems)
                click(994, 560)
                time.sleep(0.2)
                click(994, 560)
                time.sleep(0.2)
                click(994, 560)
                time.sleep(0.2)
                # click x on upgrade
                click(1104, 207)
                time.sleep(0.2)
                # click x on towers
                click(1357, 116)
                time.sleep(0.2)
        
        print("click 'Battle'")
        click(1318, 771)
        time.sleep(1)
        
    # click "2x"
    if check_color(78, 759, [0, 0, 0]):
        print("click '2x'")
        click(78, 759)
        time.sleep(1)
    
    # where is the diamond?
    # TODO if check_color(354, 713, [167, 118, 59]) and check_color(415, 121, [167, 167, 167]) and check_color(934, 222, [223, 223, 223]):
        # don't click start if we have a timer "time left"
        # TODO if not check_color(416, 618, [219, 219, 219]):
    print("solving where the diamond is")
    click(348, 751)
    solve_where_is_the_diamond()
            
    # get the color of a pixel
    # print(get_color(934, 222))

    time.sleep(1)
    move_mouse_to(100, 100)
    time.sleep(1)
    move_mouse_to(200, 200)

print("done")
