import cv2
import numpy as np
from math import sin, cos, radians
from computer_vision.object import CVBrick, CVRobot
from computer_vision.until import angleBetweenPoints
from computer_vision.wayfinder import compute_instructions
from command import Command
import pickle

colors = [[24, 75, 126, 80, 255, 255]]

def run_with_robot(robot):
    cap = cv2.VideoCapture(robot.camera)

    cmd_count = 0
    cmds = {c: 0 for c in list(Command)}

    while True:
        success, img = cap.read()
        if not success:
            print("could not read image from source: " + robot.camera)
            continue

        objs = list(detect_objects(img, colors))
        
        # select a target brick and robot form the detected objects
        cv_robot = None
        cv_brick = None
        for obj in objs:
            if obj.__class__ == CVRobot:
                cv_robot = obj
            elif obj.__class__ == CVBrick:
                cv_brick = obj

        cmd = compute_instructions(cv_brick, cv_robot)
        cmd_count += 1
        if cmd:
            cmds[cmd] += 1

        if cmd_count == 10:
            cmd_count = 0
            sent = False
            for (c, n) in cmds.items():
                if n >= 8:
                    sent = True
                    robot.conn.sendall(pickle.dumps(c))
                    break
            print(cmds)
            cmds = {c: 0 for c in list(Command)}
            if not sent:
                robot.conn.sendall(pickle.dumps(Command.STOP))


def debug(source, colors = colors):
    cap = cv2.VideoCapture(source)

    cmd_count = 0
    cmds = {"turnLeft": 0, "turnRight": 0, "moveForward": 0, "moveBackward": 0}

    while True:
        success, img = cap.read()
        if not success:
            print("could not read image from source: " + source)
            continue

        objs = list(detect_objects(img, colors))
        
        # select a target brick and robot form the detected objects
        cv_robot = None
        cv_brick = None
        for obj in objs:
            if obj.__class__ == CVRobot:
                cv_robot = obj
            elif obj.__class__ == CVBrick:
                cv_brick = obj
        
        cmd = compute_instructions(cv_brick, cv_robot, img)
        print(cmd)
        #cmd_count += 1
        #if cmd:
        #    cmds[cmd] += 1

        #if cmd_count == 10:
        #    cmd_count = 0
        #    sent = False
        #    for (k, v) in cmds.items():
        #        if v >= 8:
        #            sent = True
        #            print(k)
        #            break
        #    cmds = {key: 0 for key in cmds}
        

        cv2.imshow("Result", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            break


def detect_objects(img, colors):
    # convert to (Hue, Saturation, Value) format
    imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    for color in colors:
        # the mask consists only of colors in the range defined by the hue,sat,and val ranges
        lower = np.array(color[0:3])
        upper = np.array(color[3:6])
        mask = cv2.inRange(imgHSV, lower, upper)

        objs = detect(mask)
        for obj in objs:
            yield obj


def detect(mask):
    contours, hierarchy = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    for i in range(len(contours)):
        # rect of type: (center(x, y), (width, height), angle of rotation)
        rect = cv2.minAreaRect(contours[i])
        width, height = rect[1]
        if width * height < 860:  # ignore small objects
            continue
        
        # get points defining polygon
        epsilon = 0.05 * cv2.arcLength(contours[i], True)
        points = cv2.approxPolyDP(contours[i], epsilon, True)

        # print("obj {}".format(len(points)))
        if len(points) == 3:
            cv_robot = handle_triangle(points)
            yield cv_robot

        elif len(points) == 4:
            cv_brick = handle_square(points, rect)
            yield cv_brick


def handle_triangle(points):
    min_angle = 360
    min_point_index = 0
    for i in range(len(points)):
        a = points[(i+0) % 3][0]
        b = points[(i+1) % 3][0]
        c = points[(i+2) % 3][0]
        angle = angleBetweenPoints(a, b, c)

        if angle < min_angle:
            min_angle = angle
            min_point_index = (i+1) % 3  # aka index of point b

    front_point = points[min_point_index][0]
    p1, p2 = points[(min_point_index + 1) %
                    3][0], points[(min_point_index + 2) % 3][0]
    mid_point = ((p1[0] + p2[0])//2, (p1[1]+p2[1])//2)

    robot_mid_point = mid_point
    robot = CVRobot(robot_mid_point, [p for [p] in points], front_point)
    return robot


def handle_square(points, rect):
    brick = CVBrick(rect)
    return brick
