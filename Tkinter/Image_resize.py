import cv2

img = cv2.imread('P1-133.png')

fx = 0.5
fy = 0.5

enlarge = cv2.resize(img, (0, 0), fx=fx, fy=fy, interpolation=cv2.INTER_CUBIC)
cv2.imshow("enlarge", enlarge)