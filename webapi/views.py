from  webapi import api
# from celery import Celery

from   flask import Blueprint,Response
import numpy as np
import cv2

import webapi.utils.lib_images_io as lib_images_io
import webapi.utils.lib_plot as lib_plot
import webapi.utils.lib_commons as lib_commons
from   webapi.utils.lib_openpose import SkeletonDetector
from   webapi.utils.lib_tracker import Tracker
from   webapi.utils.lib_tracker import Tracker
from   webapi.utils.lib_classifier import ClassifierOnlineTest
from   webapi.utils.lib_classifier import *  # Import all sklearn related libraries

import webapi.Multi_person_classifier
from   webapi.Multi_person_classifier import *
import webapi.image_loader
from   webapi.image_loader import *

import webapi.utils 
from   webapi.utils import *

import webapi.utils.Dominant_color
from   webapi.utils.Dominant_color import *

import webapi.utils.Player_frame_extractor
from   webapi.utils.Player_frame_extractor import *


import webapi.utils.hex_code_validation
from   webapi.utils.hex_code_validation import *


import numpy as np
import os
import sys
import tensorflow as tf
import cv2
import argparse
import imutils
from   sklearn.cluster import KMeans
import matplotlib.pyplot as plt

import re



from   flask_ngrok import run_with_ngrok
from   flask import Flask
import re

# from webapi import cache
# from api import socketio


from werkzeug.utils import secure_filename
from flask import request, jsonify, render_template,  send_from_directory

import requests
import numpy as np
import pickle

from   PIL import Image
import math
import os
import yaml



mod = Blueprint('model', __name__, template_folder="templates")

UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = set(['mp4','avi','mpg'])
DEBUG = True


# # Initialize Celery
# celery = Celery("api.name", broker=api.config['CELERY_BROKER_URL'])
# celery.conf.update(api.config)

# app.config.from_object(__name__)
# api.config['SECRET_KEY'] = "K\x98\xa3\x89s\x146=\xe5\x97s\x17"
# api.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@mod.after_request
def after_request(response):
    response.headers.add('Accept-Ranges', 'bytes')
    return response

@mod.route('/image_frame',methods=['GET'])
def image_frame():
    DST_FOLDER = api.config["BASE_DIR"]+ "/"+"webapi/static/"
    DST_VIDEO_NAME = cfg["output"]["video_name"]
    
    full_path = DST_FOLDER+DST_VIDEO_NAME
    
    file_size = os.stat(full_path).st_size
    start = 0
    length = 10240  # can be any default length you want

    range_header = request.headers.get('Range', None)
    if range_header:
        m = re.search('([0-9]+)-([0-9]*)', range_header)  # example: 0-1000 or 1250-
        g = m.groups()
        byte1, byte2 = 0, None
        if g[0]:
            byte1 = int(g[0])
        if g[1]:
            byte2 = int(g[1])
        if byte1 < file_size:
            start = byte1
        if byte2:
            length = byte2 + 1 - byte1
        else:
            length = file_size - start

    with open(full_path, 'rb') as f:
        f.seek(start)
        chunk = f.read(length)

    rv = Response(chunk, 206, mimetype='video/mp4', content_type='video/mp4', direct_passthrough=True)
    rv.headers.add('Content-Range', 'bytes {0}-{1}/{2}'.format(start, start + length - 1, file_size))
    return rv

@mod.route('/')
def home():
    return render_template('index.html',model={'dribbling':{'count':0},'kicking':{'count':0},'passing':{'count':0},'running':{'count':0}}, image_url="")


@mod.route('/analyze_video',methods=['POST','GET'])
def analyze_video():
     if request.method == "POST":
        file = request.files['file']
        print("request_form is:",request.form)
        team1_color = request.form.get('team1')
        
        team2_color = request.form.get('team2')
        rgb_color_team1,rgb_color_team2 = validate_hex_code(team1_color,team2_color)
        print("This is rgb_color_team1",rgb_color_team1)
        print("This is rgb_color_team2",rgb_color_team2)
        
        # return jsonify(team1_color,team2_color),200
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
           
           
            results = process_score_image_request(filename,rgb_color_team1,rgb_color_team2)
            
            # results = cache.get("action_metrics")
    
            return jsonify(results),200 
    
        else:
            return jsonify("invalid file"), 400
           
        return jsonify("unknown error occured"), 500
            

           
        
            
    #  return render_template('index.html',model=action_metrics,image_url=api.config["BASE_DIR"]+"/"+"api/static/video_output/file.png")
    
@mod.route('/metrics',methods=['GET'])
def metrics():
    
    results = cache.get("action_metrics")
    
    return jsonify(results),200 



# @celery.task
def process_score_image_request(filename,rgb_color_team1,rgb_color_team2):
    
    action_metrics={'team1':{'dribbling':{'count':0},'kicking':{'count':0},'passing':{'count':0},'running':{'count':0}},'team2':{'dribbling':{'count':0},'kicking':{'count':0},'passing':{'count':0},'running':{'count':0}}}
    
    # create config
    cfg_all = lib_commons.read_yaml("config/config.yml")
    cfg = cfg_all["s5_test.py"] 
    CLASSES = np.array(cfg_all["classes"])

  
    SRC_MODEL_PATH  = api.config["BASE_DIR"]+"/webapi/model/trained_classifier.pickle"
    SRC_DATA_TYPE   = "video"
    SRC_DATA_PATH   = api.config["BASE_DIR"]+"/"+UPLOAD_FOLDER+filename
    print("this is the source data path",SRC_DATA_PATH)
    DST_FOLDER_NAME = get_dst_folder_name(SRC_DATA_TYPE, SRC_DATA_PATH)


    # Action recognition: number of frames used to extract features.
    WINDOW_SIZE = int(cfg_all["features"]["window_size"])

    # Output folder
    DST_FOLDER = api.config["BASE_DIR"]+ "/"+"webapi/static/"
    DST_SKELETON_FOLDER_NAME = cfg["output"]["skeleton_folder_name"]
    DST_VIDEO_NAME = cfg["output"]["video_name"]
    # framerate of output video.avi
    DST_VIDEO_FPS = float(cfg["output"]["video_fps"])
    



    # Openpose settings
    OPENPOSE_MODEL = cfg["settings"]["openpose"]["model"]
    OPENPOSE_IMG_SIZE = cfg["settings"]["openpose"]["img_size"]
    #add action dict

    skeleton_detector = SkeletonDetector(OPENPOSE_MODEL, OPENPOSE_IMG_SIZE)

    multiperson_tracker = Tracker()

    multiperson_classifier = MultiPersonClassifier(SRC_MODEL_PATH, CLASSES)

    images_loader = select_images_loader(SRC_DATA_TYPE, SRC_DATA_PATH)


    os.makedirs(DST_FOLDER, exist_ok=True)
    # os.makedirs(DST_FOLDER + DST_SKELETON_FOLDER_NAME, exist_ok=True)

    #Uncomment if you want to save the video bounding box
    # video writer
    video_writer = lib_images_io.VideoWriter(DST_FOLDER + DST_VIDEO_NAME, DST_VIDEO_FPS)
    
    # rgb_color_team1,rgb_color_team2
    # -- Read images and process
    try:
        ith_img = -1
        team_category = {'team1':[],'team2':[]}
        team_players = []
        total_actions = 0
        
        #Apend the rgb values for both team 1 and team2 respectively to their team category
        team_category['team1'].append(rgb_color_team1)
        team_category['team2'].append(rgb_color_team2)
        
        
        while images_loader.has_image():
            # -- Read image
            img = images_loader.read_image()
            ith_img += 1
            img_disp = img.copy()
            #Get cropped images

            print(f"\nProcessing {ith_img}th image ...")
            
                # -- Detect skeletons
            humans = skeleton_detector.detect(img)
            
            
            skeletons, scale_h = skeleton_detector.humans_to_skels_list(humans)

            skeletons = remove_skeletons_with_few_joints(skeletons)
            
    
            # for i in range(len(humans)):
            #     print("human at index i is:",humans[i])
                
            #     dominant_color = get_dominant_color(humans[i])
                
            #     if not team_category["team1"]:
            #         team_category["team1"] = dominant_color
            #     elif not team_category["team2"]:
            #         team_category["team2"] = dominant_color
                  
            #     if dominant_color == team_category["team1"]:
            #         team_players.push(1)
            #     elif dominant_color == team_category["team2"]:
            #         team_players.push(2)
            #     else:
            #         print("Save to categorized player:",dominant_color)
                

            # -- Track people
            
            dict_id2skeleton = multiperson_tracker.track(skeletons)  # int id -> np.array() skeleton
            
            # for i in dict_id2skeleton:
            #     return i
                

                        # -- Recognize action of each person
            if len(dict_id2skeleton):
                dict_id2label = multiperson_classifier.classify(
                    dict_id2skeleton)
                print("dict_id2labe is:",dict_id2label)

            

                # print("These are the cropped images",cropped_image) 
          
                cropped_image = calculate_action_metrics(img_disp.copy(),dict_id2label,dict_id2skeleton,scale_h,
                team_category,team_players,action_metrics)
            
                                   ##-- Draw
                img_disp = draw_result_img(img_disp, ith_img, humans, dict_id2skeleton,
                                            skeleton_detector, multiperson_classifier,dict_id2label,scale_h)
                
            
                video_writer.write(img_disp)
                
                    
                
                # @mod.route('/video/<string:file_name>')
                # def stream(file_name):
                #     video_dir = DST_FOLDER
                #     return send_from_directory(directory=video_dir, filename=file_name)

            
            print(f'team_players of {len(team_players)}:',team_players)
            
            
            
            #fix later
            # if True:
            #     key_index=-1
            #     for key in dict_id2skeleton.keys():
            #         key_index +=1
            #         print("key is:",key_index)
            #         print("dict_id2_label.key is:",dict_id2label[key])
                    
            #         # action_metrics = cache.get("action_metrics")
            #         if dict_id2label[key] in action_metrics["team1"]:
            #             total_actions += 1
                        
                        # if team_players[key_index] == 1:
                        #     action_metrics["team1"][dict_id2label[key]]["count"]+=1
                        #     print("prediced label team1 is :",action_metrics["team1"][dict_id2label[key]])
                            
                        # elif team_players[key_index] == 2:
                        #     action_metrics["team2"][dict_id2label[key]]["count"]+=1
                        #     print("prediced label team2 is :",action_metrics["team2"][dict_id2label[key]])
                    
                #   cache.set("action_metrics",action_metrics)
        
                  
                  
            # if len(dict_id2skeleton):
            #   for key in dict_id2skeleton.keys():
            #     print("key is:",key)
            #     if dict_id2label[key] in action_metrics:
            #       action_metrics[dict_id2label[key]]['count']+=1
            #       print("prediced label is :", action_metrics[dict_id2label[key]])
            #       socketio.emit(dict_id2label[key],{count:action_metrics[dict_id2label[key]]['count']})
            #     min_id = min(dict_id2skeleton.keys())
            #     if dict_id2label[min_id] in action_metrics:
            #         action_metrics[dict_id2label[min_id]]['count']+=1
            #         print("prediced label is :", action_metrics[dict_id2label[min_id]])
               



    # Uncomment if you want to save the video boundary box


                # -- Display image, and write to video.avi
    #           img_displayer.display(img_disp, wait_key_ms=1)
                

    #         # -- Get skeleton data and save to file
    #         skels_to_save = get_the_skeleton_data_to_save_to_disk(
    #             dict_id2skeleton)
    #         lib_commons.save_listlist(
    #             DST_FOLDER + DST_SKELETON_FOLDER_NAME +
    #             SKELETON_FILENAME_FORMAT.format(ith_img),
    #             skels_to_save)
        
        print("total actions detected: ", total_actions)
        
    finally:
        
        ##Uncomment if you want to save the video boundary box
        video_writer.stop()
        # 
        print("Program ends")
    return action_metrics
        # video_url=""
        # import base64
        # with open(DST_FOLDER + DST_VIDEO_NAME, "rb") as videoFile:
        #   video_url = base64.b64encode(videoFile.read())