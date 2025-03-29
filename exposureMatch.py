import cv2
import numpy as np
import os
import time
import re

import matplotlib.pyplot as plt
from skimage import exposure
from skimage.exposure import match_histograms

from glob import glob
from vidgear.gears import WriteGear
from tqdm import tqdm

def ensure_directory(directory):
         if not os.path.exists(directory):
              os.makedirs(directory)
    
def get_next_image_index(directory):
   files = sorted(os.listdir(directory))
   image_files = [f for f in files if f.startswith("image-") and f.endswith(".jpg")]
   if image_files:
       indices = [int(f.split('-')[1].split('.')[0]) for f in image_files]
       return max(indices) + 1
   return 0

def loop_function(reference_img, source_img):
    
    multi = True if source_img.shape[-1] > 1 else False
    matched_img = exposure.match_histograms(source_img, reference_img,multichannel=multi)
    matched = match_histograms(matched_img, reference_img, multichannel=multi)
    
    return matched

def extract_number(file_path):
    match = re.search(r'(\d+)', file_path)
    if match:
        return int(match.group(1))
    else:
        return -1 
    
if __name__ =="__main__":
    print("Starting Code")

    DIRECTORY ="capture"
    COLOR_GRADED_DIRECTORY = "capture-color-graded"

    files = sorted(glob(f'{DIRECTORY}/*.jpg'),key=extract_number)

    reference = cv2.imread(f'capture/image-1.jpg')
    print("Copying reference image to new directory")
    #cv2.imwrite(f'{COLOR_GRADED_DIRECTORY}/image-0.jpg', reference)

    for file in tqdm(files, desc="Color grading pictures..."):
        
        source = cv2.imread(file)
        machted_img = loop_function(reference,source)
        h_z = np.hstack((source,machted_img))
        #cv2.imshow("Color Grading", h_z)
        #cv2.waitKey(0)
        #cv2.destroyWindow("Color Grading")
        image_index = get_next_image_index(COLOR_GRADED_DIRECTORY)
        cv2.imwrite(f'{COLOR_GRADED_DIRECTORY}/image-{image_index}.jpg', machted_img)
    #cv2.destroyAllWindows()
    print("Finished color grading.")

    
         



