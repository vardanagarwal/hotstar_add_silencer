import argparse
import os
import shutil

import cv2
import numpy as np
import pandas as pd
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument('--input_folder', required=True, help='path to input folder or input video. Please make sure the path is in the working directory')
parser.add_argument('--output_folder', default='selected', help='path to output folder')
parser.add_argument('--unwanted_folder', default='unwanted', help='path to unwanted folder')
parser.add_argument('--temporary_image_folder', default='temporary_video_to_image_folder', help='path to temporary folder to store image frames of video')
parser.add_argument('--model', default=None, help='path to model for detection')
parser.add_argument('--second_model', default=None, help='path to second model for detection. Only checked if model is passed')
parser.add_argument('--conf', default=0.25, type=float, help='minimum confidence of person detection')
parser.add_argument('--stride', default=1, type=int, help='to take a stride over the list of images')
parser.add_argument('--skip', default=20, type=int, help='number of frames to skip on p')

args = parser.parse_args()

input_folder = args.input_folder
input_video = input_folder.split('/')[-1]
output_folder = args.output_folder
unwanted_folder = args.unwanted_folder
temp_folder_name = args.temporary_image_folder
stride = args.stride
model_detection = False
second_model_detection = False
gap = 5

if input_folder.endswith(".mp4") or input_folder.endswith(".avi"):
    cap = cv2.VideoCapture(input_folder)
    if not os.path.exists(temp_folder_name):
        os.makedirs(temp_folder_name)
    if not len(os.listdir(temp_folder_name)):
        print("extracting images from video")
        for i in tqdm(range(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)))):
            ret, img = cap.read()
            if ret:
                cv2.imwrite(os.path.join(temp_folder_name, input_folder[:-4] + '_' + '0'*(6-len(str(i))) + str(i) + '.jpg'), img)
            else:
                break
    input_folder = temp_folder_name
        
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

if not os.path.exists(unwanted_folder):
    os.makedirs(unwanted_folder)

# if not os.path.exists(args.videos):
#     os.makedirs(args.videos)

if args.model != None:
    from detect_selector import infer_single
    obj = infer_single(args.model)
    model_detection = True
    if args.second_model != None:
        obj2 = infer_single(args.second_model)
        second_model_detection = True

images = os.listdir(input_folder)
images.sort()
select_count = len(os.listdir(output_folder))
frame_count = len(os.listdir(output_folder)) + len(os.listdir(unwanted_folder))
if input_folder == output_folder:
    select_count = 0
if input_folder == unwanted_folder:
    frame_count = 0

i = frame_count
font = cv2.FONT_HERSHEY_SIMPLEX
list_events = []
images = [np.zeros((10, 10), dtype=np.uint8)]*frame_count + images
num_frames = len(images)

while i < num_frames + frame_count:
    try:
        image = images[i]
    except:
        break
    img = cv2.imread(os.path.join(input_folder, image))
    try:
        h, w = img.shape[:2]
        h_org, w_org = h, w
    except:
        print(image + ' this image is not correct, pls delete and start again')
        exit
    r = 1
    if max(w, h) > 1200:
        r = 1200/ max(w, h)
    elif min(w, h) < 1000:
        r = 1000/ min(w, h)
    img = cv2.resize(img, None, fx=r, fy=r)
    h, w = img.shape[:2]
    counts = np.zeros((40, w, 3), dtype=np.uint8)
    cv2.putText(counts, 'image count: ' + str(frame_count) + ' ' + 'Selected images count: ' + str(select_count),
                (10, 25), font, 1, (255, 255, 255), 2)

    cv2.putText(img, str(i), (10, 45), font, 2, (0, 255, 255), 2)
    img = cv2.vconcat([counts, img])
    cv2.imshow('selector', img)
    a = cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # end with esc
    if a == 27:
        break

    # save with s
    elif a == 115:
        # out = cv2.VideoWriter(os.path.join(args.videos, input_video[:-4] + str(i).zfill(6) + '.mp4'), cv2.VideoWriter_fourcc(*'mp4v'), 1, (w_org, h_org))
        os.rename(os.path.join(input_folder, image), os.path.join(output_folder, image))
        # for k in range(i, i + 100):
        #     try:
        #         image = images[k]
        #         out.write(cv2.imread(os.path.join(input_folder, image)))
        #         os.rename(os.path.join(input_folder, image), os.path.join(output_folder, image))
        #     except:
        #         break
        # i += 1
        # frame_count += 1
        # out.release()
        select_count += 1
        for j in range(1, stride):
            try:
                image = images[i + j]
                os.rename(os.path.join(input_folder, image), os.path.join(unwanted_folder, image))
            except:
                break
        frame_count += stride
        i += stride
    
    # go forward with ->
    elif a == 83:
        os.rename(os.path.join(input_folder, image), os.path.join(unwanted_folder, image))
        for j in range(1, stride):
            try:
                image = images[i + j]
            except:
                break
            os.rename(os.path.join(input_folder, image), os.path.join(unwanted_folder, image))
        frame_count += stride
        i += stride
    
    # go back with <-
    elif a == 81:
        i -= 1
        image = images[i]
        if os.path.isfile(os.path.join(unwanted_folder, image)):
            os.rename(os.path.join(unwanted_folder, image), os.path.join(input_folder, image))
            frame_count -= 1

        elif os.path.isfile(os.path.join(output_folder, image)):
            os.rename(os.path.join(output_folder, image), os.path.join(input_folder, image))
            frame_count -= 1
            select_count -= 1
        
        for event in list_events:
            if event[0] > i:
                list_events.remove(event)

    # move all with e
    elif a == 101:
        cv2.putText(img, 's: select all, d: reject all, other keys: cancel', (10, 50), font, 1, (0, 0, 0), 2, cv2.LINE_AA)
        cv2.putText(img, 's: select all, d: reject all, other keys: cancel', (10, 50), font, 1, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.imshow('image count: ' + str(frame_count) + ' ' + 'Selected images count: ' + str(select_count), img)
        a = cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        # move all to selected folder with s
        if a == 115:
            for j in range(i, len(images)):
                image = images[j]
                os.rename(os.path.join(input_folder, image), os.path.join(output_folder, image))
            break
        # move all to unwanted folder with d
        elif a == 100:
            for j in range(i, len(images)):
                image = images[j]
                os.rename(os.path.join(input_folder, image), os.path.join(unwanted_folder, image))
            break
    
    # skip args.skip frames with p
    elif a == 112:
        j = i + args.skip
        while i < j:
            try:
                image = images[i]
                os.rename(os.path.join(input_folder, image), os.path.join(unwanted_folder, image))
                i += 1
                frame_count += 1
            except:
                break

    # move all frames till the next one with no persons in the unwanted folder with m
    elif a == 109:
        if not model_detection:
            cv2.putText(img, 'Pass model argument to use this', (10, 50), font, 1, (0, 0, 0), 2, cv2.LINE_AA)
            cv2.imshow('image count: ' + str(frame_count) + ' ' + 'Selected images count: ' + str(select_count), img)
            a = cv2.waitKey(0)
            cv2.destroyAllWindows()
        else:
            pbar = tqdm()
            while True:
                if obj.run(img, args.conf) or (second_model_detection and obj2.run(img, args.conf)):
                    break
                os.rename(os.path.join(input_folder, image), os.path.join(unwanted_folder, image))
                i += 1
                frame_count += 1
                image = images[i]
                img = cv2.imread(os.path.join(input_folder, image))
                pbar.update(1)
            pbar.close()

cv2.destroyAllWindows()

if os.path.exists(temp_folder_name):
    if not len(os.listdir(temp_folder_name)):
        os.rmdir(temp_folder_name)
        # shutil.rmtree(unwanted_folder)
