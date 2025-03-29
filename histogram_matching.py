import cv2
import matplotlib.pyplot as plt
import numpy as np
from skimage import exposure
from skimage.exposure import match_histograms


reference = cv2.imread( "capture/image-1.jpg")
original = cv2.imread("capture/image-100.jpg")
img_hsv = cv2.cvtColor(reference, cv2.COLOR_BGR2HSV)

#Equalise chanel v
img_hsv[:,:,2] = cv2.equalizeHist(img_hsv[:,:,2])
equ_out = cv2.cvtColor(img_hsv, cv2.COLOR_HSV2BGR)

cv2.imshow("Equalised", np.hstack((reference,equ_out)) )
cv2.waitKey(0)
cv2.destroyAllWindows()

matched = match_histograms(original, reference, multichannel=True)
cv2.imshow("Histogram Match", np.hstack((reference,original, matched)))
cv2.waitKey(0)
cv2.destroyAllWindows()