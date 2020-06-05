from   webapi import api

import cv2
import utils.lib_commons as lib_commons
from   webapi.utils.Dominant_color import *
from   webapi.utils.color_threshold import *
import webapi.utils.hex_code_validation
from   webapi.utils.hex_code_validation import *

 
 # create config
cfg_all = lib_commons.read_yaml("config/config.yml")
cfg = cfg_all["s5_test.py"]

img_disp_desired_rows = int(cfg["settings"]["display"]["desired_rows"])


def calculate_action_metrics(img_display,dict_id2label,dict_id2skeleton,scale_h,team_category,team_players,action_metrics):
                
    i = 0
    NaN = 0
    
    # Resize to a proper size for display
    r, c = img_display.shape[0:2]
    desired_cols = int(1.0 * c * (img_disp_desired_rows / r))
    img_display = cv2.resize(img_display,dsize=(desired_cols, img_disp_desired_rows))
    
        
    if len(dict_id2skeleton):
        for id, label in dict_id2label.items():
            minx = 999
            miny = 999
            maxx = -999
            maxy = -999
            
            skeleton = dict_id2skeleton[id]
            # scale the y data back to original
            skeleton[1::2] = skeleton[1::2] / scale_h

            while i < len(skeleton):
                if not(skeleton[i] == NaN or skeleton[i+1] == NaN):
                    minx = min(minx, skeleton[i])
                    maxx = max(maxx, skeleton[i])
                    miny = min(miny, skeleton[i+1])
                    maxy = max(maxy, skeleton[i+1])
                i += 2
                
            minx = int(minx * img_display.shape[1])
            miny = int(miny * img_display.shape[0])
            maxx = int(maxx * img_display.shape[1])
            maxy = int(maxy * img_display.shape[0])
            
            
            ROI= img_display[miny:maxy,minx:maxx]
            
            print("total skeleton is", len(skeleton))
            
            print("ROI is:", ROI)
            
            try:
                if len(ROI):
                    cv2.imwrite(api.config["BASE_DIR"]+f"/webapi/static/video_output/roi{str(id)}.png",ROI) 
                    
                    dominant_color = get_dominant_color(api.config["BASE_DIR"]+f"/webapi/static/video_output/roi{str                     (id)}.png")
                    
                    
                            
                    # if  len(team_category["team1"]) == 0:
                    #     team_category["team1"] = dominant_color
                    #     print("this is team_category1:",team_category["team1"])
                        
                    # elif len(team_category["team2"])==0:
                    #     team_category["team2"] = dominant_color
                    #     print("this is team_category1:",team_category["team2"])
                       
                    '''
                    rgb_color_difference for team1 using the hex color code gotten from UI
                    After converting to rgb color code    
                
                    '''
                    
                    rgb_color_difference_team1 = get_rgb_color_difference(dominant_color,team_category["team1"][0])
                    print("This is the rgb_difference:",rgb_color_difference_team1)
                    
                    
                    '''
                    rgb_color_difference for team2 using the hex color code gotten from UI
                    After converting to rgb color code    
                
                    '''
                    
                    rgb_color_difference_team2 = get_rgb_color_difference(dominant_color,team_category["team2"][0])
                    print("This is the rgb_difference:",rgb_color_difference_team2)
                    
                    
                      
                    #thresholding for team 1
                    if rgb_color_difference_team1 <= 70:
                        team1_action_metrics = action_metrics["team1"][dict_id2label[id]]["count"]+=1
                        print("This is team1_action_metrics: ",team1_action_metrics)
                     
                    #thresholding for team 2    
                    elif rgb_color_difference_team2 <= 70 :
                       team2_action_metrics = action_metrics["team2"][dict_id2label[id]]["count"]+=1
                       print("This is team2_action_metrics: ",team2_action_metrics)
                       
                    else:
                       print("Failed to categorize player's dominant color:",dominant_color)   
                       
                    # team_players.append(1)   
                    #   team_players.append(2) 
                        
                    # if dominant_color == team_category["team1"]:

                    #     team_players.append(1)
                        
                        
                    # elif dominant_color == team_category["team2"]:
                    #     team_players.append(2)
                    # else:
                    #     print("Save to categorized player:",dominant_color)
                    
                    
                else:
                    print("empty image display is", ROI)
                    
            except Exception as ex:
                        print ("an error occured",str(ex))