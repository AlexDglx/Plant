## Alex Degallaix - 2023
# All rights reserved
# Purpose : This script is automatically take pictures of a growing plant to produce a stop motion film
#!/usr/bin/python

import cv2
import numpy as np
import time
import pickle
import os
import urllib
import datetime
import requests
import json
from pathlib import Path
from os import walk

from phue import Bridge
from datetime import timedelta
from astral import LocationInfo
from astral.sun import sun

#get current date
SMART_PLUG_NAME = 'Hue smart plug 1'
CALIBRATION = "calibration.dat"

class systemFile:
    @staticmethod
    def ensure_directory(directory):
         if not os.path.exists(directory):
              os.makedirs(directory)
    @staticmethod
    def get_next_image_index(directory):
       files = os.listdir(directory)
       image_files = [f for f in files if f.startswith("image-") and f.endswith(".jpg")]
       if image_files:
           indices = [int(f.split('-')[1].split('.')[0]) for f in image_files]
           return max(indices) + 1
       return 0
     

class imageCapture:
    @staticmethod
    def undstrt(frame, cameraMatrix, newCameraMatrix,distortionMatrix, imageWidth, imageHeight):

        # return the undistorted image
        mapx, mapy = cv2.initUndistortRectifyMap(newCameraMatrix,distortionMatrix,None,cameraMatrix, (imageWidth,imageHeight),5)
        dst = cv2.remap(frame, mapx, mapy, cv2.INTER_LINEAR)

        return dst
   
    @staticmethod
    def capture(directory,cameraMatrix,newCameraMatrix,distortionMatrix):
        
        systemFile.ensure_directory(directory)

        image_index = systemFile.get_next_image_index(directory)
        
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            print('Could not open camera')
            return 
        ret, frame = camera.read()
    
        if not ret:
            print("Failed to get webcame frame")
            return
        
        dst_frame1 = imageCapture.undstrt(frame, cameraMatrix, newCameraMatrix,distortionMatrix, frame.shape[1], frame.shape[0])
        crop_img = dst_frame1[25:900, 600:1250]
        final = imageCapture.blur_and_sharpen_background(crop_img, low_threshold=100, high_threshold=215, blur_strength=(7, 7), alpha=0.5)
        filename = os.path.join(directory, f"image-{image_index}.jpg")
        #image 105 change of image processing
        cv2.imwrite(filename, final)
        camera.release()
        print(f'Picture taken and saved as {filename}')
        return [final,image_index]

    @staticmethod
    def lights(state, lightName):

        b = Bridge("192.168.1.67")
        b.connect()
        light = b.get_light_objects('name')
        light[lightName].on = state

        return state
    
    @staticmethod
    def blur_and_sharpen_background(img:np.ndarray, low_threshold=100, high_threshold=215, blur_strength=(7, 7), alpha=0.5):
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, low_threshold, high_threshold)
        kernel = np.ones((5,5), np.uint8)
        dilated_edges = cv2.dilate(edges, kernel, iterations=1)
        mask = np.zeros_like(img)
        mask[dilated_edges != 0] = [255, 255, 255]
        
        mask_inv = cv2.bitwise_not(mask)
        blurred = cv2.GaussianBlur(img, blur_strength, 0)

        kernel_sharpening = np.array([[-1, -1, -1],
                                    [-1,  9, -1],
                                    [-1, -1, -1]])
        sharpened = cv2.filter2D(img, -1, kernel_sharpening)
        softened_sharpened = cv2.addWeighted(img, alpha, sharpened, 1 - alpha, 0)
        foreground = cv2.bitwise_and(softened_sharpened, mask)
        background = cv2.bitwise_and(blurred, mask_inv)
        final = cv2.add(foreground, background)

        return final
    
class calibrationFile:
    @staticmethod
    def readCalibrationFile(PATH: str) -> list:
        with open(PATH, 'rb') as f:    
            list = pickle.load(f)
        return list

class timeSun:
    @staticmethod
    def get_target_times():

        city = LocationInfo("Vancouver", "Canada", "America/Vancouver", 49.26,-123.08)
        s = sun(city.observer, date=datetime.date.today(), tzinfo=city.timezone)
        before_sunrise = s['sunrise']-datetime.timedelta(hours=2)
        sunrise_time = s['sunrise']+datetime.timedelta(hours=2)
        noon_time = datetime.datetime.combine(datetime.date.today(), datetime.time(12, 0))
        sunset_time = s['sunset'] - datetime.timedelta(hours=2)
        after_sunset = s['sunset'] + datetime.timedelta(hours=2)
        planification = s['sunrise'] - datetime.timedelta(hours=30,minutes=0, seconds=36)
        print(f'Send message give schedule {planification}')

        return [[planification.time(),before_sunrise.time(),s['sunrise'].time(),sunrise_time.time(),noon_time.time(),(noon_time+datetime.timedelta(hours=2)).time(),(noon_time+datetime.timedelta(hours=4)).time(),(noon_time+datetime.timedelta(hours=6)).time(), sunset_time.time(),s['sunset'].time(),after_sunset.time()], planification.time(),
                f'Sunrise: 🌄 {s["sunrise"].strftime("%Y-%m-%d %H:%M:%S")} \nSunset: 🌅 {s["sunset"].strftime("%Y-%m-%d %H:%M:%S")}']

class jsonConfigFile:
    #read json file
    def readJson(jsonPath:str) -> dict:
        with open(jsonPath, "r") as file:
            a = json.load(file)
            file.close()
        return a
    
class messaging:
    @staticmethod
    def telegram(message:dict):
        token = jsonConfigFile.readJson('telegram_cred.json')
        api_key = token['telegram']['ApiKey']
        chat_id = token['telegram']['chat_id']

        
        url = 'https://api.telegram.org/bot%s/sendMessage?chat_id=%s&text=%s' % (
        
        api_key, chat_id, urllib.parse.quote_plus(f'{message["Title"]}\n\n{message["Body"]}'))
        _ = requests.get(url, timeout=10)

if __name__ =="__main__":
    start = time.perf_counter()
    #turn light of if on 
    
    state = imageCapture.lights(False, SMART_PLUG_NAME)
    print(f'Lights state: {state}')
    #Opening camera calibration file
    camera_details =  calibrationFile.readCalibrationFile(CALIBRATION)

    print("Press 'q' to quit the script." )
    DIRECTORY="capture"

    #get target time
    target_times = timeSun.get_target_times()
    print(target_times[0])
    taken_today = set()

    time.sleep(2)

    message = {
                    "Title":f'😄 🌱 🥬  Picture:{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                    "Body": f'Launching Stop Motion \n\n💦 Water the lettuce 💦'
                }
            
    messaging.telegram(message)

    while True:
        now = datetime.datetime.now().time()
        if now >= (datetime.datetime.combine(datetime.date.today(), target_times[1]) - datetime.timedelta(seconds=2)).time() and \
            now <= (datetime.datetime.combine(datetime.date.today(), target_times[1]) + datetime.timedelta(seconds=2)).time() :

            body_message = target_times[2]

            # Ensure the directory exists
            systemFile.ensure_directory(DIRECTORY)
            # Count the number of image files
            image_count = systemFile.get_next_image_index(DIRECTORY)

            message = {
                    "Title":f'😄 🌱 🥬 Pictures Schedule:{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                    "Body": f'{body_message}\n\nPictures taken: {image_count}\n\n💦 Water the lettuce 💦'
                }
            messaging.telegram(message)

        time.sleep(1)

        for target_time in target_times[0]:

            if now >= (datetime.datetime.combine(datetime.date.today(), target_time) - datetime.timedelta(seconds=1)).time() and \
               now <= (datetime.datetime.combine(datetime.date.today(), target_time) + datetime.timedelta(seconds=1)).time() and \
               target_time not in taken_today:
                
                #turn light before camera on
                state = imageCapture.lights(True, SMART_PLUG_NAME)
                print(f'Lights state: {state}')
                captured_image = imageCapture.capture(DIRECTORY,camera_details["RawCameraMatrix"],camera_details["NewCameraMatrix"],camera_details["DistortionMatrix"])
                taken_today.add(target_time)
                imageCapture.lights(False, SMART_PLUG_NAME)
                print(f'Lights state : {state}')
                cv2.imshow("Image Captured", captured_image[0])
                
                cv2.destroyAllWindows()

        #reset the taken_Today to set at midnight
        if now >= datetime.time(0, 0) and now <= datetime.time(0, 1):
            target_times = timeSun.get_target_times()
            taken_today.clear()

        k = cv2.waitKey(1)

        if k%256 ==27:
            print('Stopping the script')
            break
        #sleep to prevent high cpu usage
        time.sleep(1) 

    end = time.perf_counter()  
    execution_time= (end -start)
    print(f'Elapsed time: {execution_time}s')

# RawCameraMatrix, DistortionMatrix, Rotation_vectors
# CalibrationError, TunedDistX, TunedDistY, NewCameraMatrix, Translation_vectors
