import cv2
import numpy as np

cap = cv2.VideoCapture(0)

# cv2.legacy.MultiTracker_create()
tracker = cv2.TrackerKCF_create()

_, preimg = cap.read()
bbox = cv2.selectROI("tracking", preimg, False)
tracker.init(preimg, bbox)

def drawBox(img, bbox):
    x,y,w,h = int(bbox[0]),int(bbox[1]),int(bbox[2]),int(bbox[3])
    cv2.rectangle(img, (x,y), ((x+w), (y+h)), (255,0,255), 3, 1)

while True:
    _, img = cap.read()
    success, bbox = tracker.update(img)

    if success:
        print(bbox)
        drawBox(img, bbox)
    else:
        print("err")

    cv2.imshow("tracking", img)
    if cv2.waitKey(1) & 0xff == ord('q'):
        break