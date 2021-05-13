import cv2
import numpy as np
from sys import float_info
from math import sqrt, atan2, degrees, isnan, isinf
from command import Command

small_float = 1/(2**16)
angle_threshold = 10 # degree
dist_threshold = 50 # pixels

def compute_instructions(cv_brick, cv_robot, img=None):
    if not cv_brick or not cv_robot:
        return None

    # c1 and c2 are define the closest long side of the brick
    c1, c2, c3, c4 = order_brick_corners(cv_brick, cv_robot)
    c12 = point_mid(c1, c2)
    c34 = point_mid(c3, c4)

    brick_dir = vector(c34, c12)
    robot_dir = vector(cv_robot.mid_point, cv_robot.front_point)

    p = line_intersection(c12, c34, cv_robot.mid_point, cv_robot.front_point)
    if isnan(p[0]) or isnan(p[0]) or isinf(p[0]) or isinf(p[1]):
        print("intersection at {}".format(p))
        return None

    angle = vector_angle(brick_dir, robot_dir)  # -180 to 180
    side_angle = vector_angle(
        vector(c34, c12), vector(cv_robot.mid_point, c12))
    isToLeft = side_angle > 0

    p_dist = point_line_distance(c12, c34, cv_robot.mid_point)
    front_to_box_dist = point_distance(cv_robot.front_point, c12)

    cmd_id = None
    if p_dist < 50:
        # the robot is on the brick line
        if front_to_box_dist < 50:
            cmd_id = Command.GRAB
        elif abs(angle) > 170:
            cmd_id = Command.DRIVE
        else:
            if angle <= 0:
                cmd_id = Command.TURN_LEFT
            else:
                cmd_id = Command.TURN_RIGHT
    else:
        # the robot should drive to the brick line
        cmd_id = move_robot_out_of_zone(cv_robot, c1, c2, c3, c4)
        if not cmd_id: 
            cmd_id = move_robot_to_line(cv_robot, c12, c34)

    # visualize
    if img is not None:
        draw_point(p, img)
        draw_vector(c34, brick_dir, 500, img)
        draw_vector(cv_robot.mid_point, robot_dir, 500, img)
        cv_brick.drawOutline(img)
        cv_robot.drawOutline(img)

    return cmd_id


def move_robot_to_line(r, p1, p2):
    # move robot to line going through p1 and p2
    dist = point_line_distance(p1, p2, r.mid_point)
    if dist < dist_threshold: 
        return None # already on line 
    
    robot_dir = vector(r.mid_point, r.front_point)
    line_dir = vector(p2, p1)

    angle = vector_angle(line_dir, robot_dir)
    is_to_left = vector_angle(line_dir, vector(r.mid_point, p1)) > 0

    if abs(angle) < 90 + angle_threshold and abs(angle) > 90 - angle_threshold:
        # drive towards line
        if angle < 0:
            if is_to_left: return Command.REVERSE
            else: return Command.DRIVE
        else:
             if not is_to_left: return Command.REVERSE
             else: return Command.DRIVE    
    else:
        # turn towards line
        if angle < 0:
            if abs(angle) > 90: return Command.TURN_RIGHT 
            else: return Command.TURN_LEFT        
        else:
            if abs(angle) < 90: return Command.TURN_RIGHT
            else: return Command.TURN_LEFT


def move_robot_out_of_zone(r, p1, p2, q1, q2):
    # move robot out of zone defined between line(p1, p2) and line(q1, q2) 
    if point_distance(r.mid_point, p1) > point_distance(r.mid_point, p2):
        p1, p2 = p2, p1
    if point_distance(r.mid_point, q1) > point_distance(r.mid_point, q2):
        q1, q2 = q2, q1

    line_dir_1 = vector(p2, p1)
    line_dir_2 = vector(q2, q1)
    is_to_left_1 = vector_angle(line_dir_1, vector(r.mid_point, p1)) > 0
    is_to_left_2 = vector_angle(line_dir_2, vector(r.mid_point, q1)) > 0
    dist_1 = point_line_distance(p1, p2, r.mid_point)
    dist_2 = point_line_distance(q1, q2, r.mid_point)
    if is_to_left_1 == is_to_left_2 and dist_1 > 5*dist_threshold and dist_2 > 5*dist_threshold:
        return None # not in the zone 

    v1 = vector(q1, p1)
    v2 = vector(q2, p2)
    o1 = [p1[0] + 10*v1[0], p1[1] + 10*v1[1]]
    o2 = [p2[0] + 10*v2[0], p2[1] + 10*v2[1]]
    return move_robot_to_line(r, o1, o2)


def order_brick_corners(brick, robot):
    points = sorted(
        brick.corners, key=lambda p: point_distance(p, robot.front_point))
    c1 = points[0]
    c4 = points[3]
    if (point_distance(c1, points[1]) > point_distance(c1, points[2])):
        c2 = points[1]
        c3 = points[2]
    else:
        c2 = points[2]
        c3 = points[1]

    # print("{},{},{},{}".format(c1,c2,c3,c4))
    return (c1, c2, c3, c4)


def vector(p1, p2):
    # p1 origin pointing towards p2
    return (p2[0] - p1[0], p2[1] - p1[1])


def vector_angle(v1, v2):
    dot = v1[0]*v2[0] + v1[1]*v2[1]
    det = v1[0]*v2[1] - v1[1]*v2[0]
    return degrees(atan2(det, dot))


def point_mid(p1, p2):
    # point between 2 points
    return ((p1[0] + p2[0])/2, (p1[1]+p2[1])/2)


def point_distance(p1, p2):
    return sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)


def point_line_distance(p1, p2, q):
    n = (p2[0]-p1[0]) * (p1[1] - q[1]) - (p1[0] - q[0]) * (p2[1]-p1[1])
    d = point_distance(p1, p2)
    return abs(n)/d


def line(p1, p2):
    # line from 2 points
    if p2[0] == p1[0]:
        slope = (p2[1] - p1[1])/small_float
    else:
        slope = (p2[1] - p1[1])/(p2[0] - p1[0])

    intercept = -p1[0] * slope + p1[1]
    return (slope, intercept)


def line_intersection(p1, p2, q1, q2):
    # intersection point between line(p1, p2) and line(q1, q2)
    a, c = line(p1, p2)  # y = ax+c
    b, d = line(q1, q2)  # y = bx+d

    if a == b:
        x = (d-c)/small_float
    else:
        x = (d-c)/(a-b)

    y = a*(x)+c
    return [x, y]


def draw_vector(p, v, length, img):
    v_len = (sqrt(v[0]**2 + v[1]**2))
    v_unit = (v[0]/v_len, v[1]/v_len)
    cv2.line(img, tuple(map(int, p)), (int(
        p[0] + length * v_unit[0]), int(p[1] + length * v_unit[1])), (10, 10, 10), 5)


def draw_point(p, img):
    cv2.circle(img, tuple(map(int, p)), 10, (50, 50, 50), 5)
