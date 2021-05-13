import cv2
import numpy as np
from math import sin, cos, radians


class CVBrick:

    def __init__(self, rect):
        self.center = rect[0]
        self.size = rect[1]
        self.angle = rect[2]
        self.corners = cv2.boxPoints(rect)

    def drawCornors(self, img):
        for corner in self.corners:
            cv2.circle(img, (corner[0], corner[1]), 10, (0, 0, 255), -1, 8)

    def drawOutline(self, img):
        box = np.int64(self.corners)
        cv2.drawContours(img, [box], 0, (0, 0, 255), 2)


class CVRobot:

    def __init__(self, mid_point, corners, front_point):
        self.mid_point = mid_point
        self.corners = corners
        self.front_point = front_point

    def drawCornors(self, img):
        for corner in self.corners:
            cv2.circle(img, (corner[0], corner[1]), 10, (0, 0, 255), -1, 8)

    def drawOutline(self, img):
        box = np.int64(self.corners)  # not sure why this is nesseary
        cv2.drawContours(img, [box], 0, (0, 0, 255), 2)
