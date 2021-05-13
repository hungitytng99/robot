# This is a small tool to find Hue, Saturation, and Value ranges to define colors
# This is heavely inspired by Murtaza Hassan
# credit: Murtaza Hassan
# https://www.murtazahassan.com/courses/learn-opencv-in-3-hours/

import numpy as np
import cv2

def empty(a):
    pass

def pick_color(source, initial_values=[0,0,0,179,255,255]):
    if source:
        cap = cv2.VideoCapture(source)
    
    # create control window
    cv2.namedWindow("HSV")
    cv2.createTrackbar("Hue min", "HSV", initial_values[0],179, empty)
    cv2.createTrackbar("SAT min", "HSV", initial_values[1],255, empty)
    cv2.createTrackbar("VAL min", "HSV", initial_values[2],255, empty)
    cv2.createTrackbar("Hue max", "HSV", initial_values[3],179, empty)
    cv2.createTrackbar("SAT max", "HSV", initial_values[4],255, empty)
    cv2.createTrackbar("VAL max", "HSV", initial_values[5],255, empty)

    while True:
        if source: 
            success, img = cap.read()
        
            if not success:
                print("error: could not read image from video source")
                return
        else: 
            img = cv2.imread("test.jpg", flags=cv2.IMREAD_COLOR)

        imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        h_min = cv2.getTrackbarPos("Hue min", "HSV")
        s_min = cv2.getTrackbarPos("SAT min", "HSV")
        v_min = cv2.getTrackbarPos("VAL min", "HSV")
        h_max = cv2.getTrackbarPos("Hue max", "HSV")
        s_max = cv2.getTrackbarPos("SAT max", "HSV")
        v_max = cv2.getTrackbarPos("VAL max", "HSV")

        lower = np.array([h_min, s_min, v_min])
        upper = np.array([h_max, s_max, v_max])
        mask = cv2.inRange(imgHSV, lower, upper)
        result = cv2.bitwise_and(img, img, mask=mask)

        mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        hStack = np.hstack([mask])
        # hStack = np.hstack([img, mask, result]) # shows more info

        cv2.imshow("what is white is being detected", hStack)    
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            if source:
                cap.release()
            cv2.destroyAllWindows()
            return [h_min, s_min, v_min, h_max, s_max, v_max]
            break


if __name__ == "__main__":
    colors = pick_color(None)
    print(colors)