import re

def validate_hex_code(team1_hex_color_code, team2_hex_color_code):
    match1 = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', team1_hex_color_code)
    match2 = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', team2_hex_color_code)
    if match1:
        print('Hex color code for team1 is valid',team1_hex_color_code)
        
    
    else:
       return 'Hex color code for team1 not is valid'
    
    if match2:
       print('Hex color code for team2 is valid',team2_hex_color_code)

        
    else:
       return 'Hex color code for team2 not is valid'
       
    hex_code_team1 = team1_hex_color_code.lstrip('#')
    hex_code_team2 = team2_hex_color_code.lstrip('#')
   
   
    RGB_Value_Team1=list(int(hex_code_team1[i:i+2], 16) for i in (0, 2, 4))
    print('RGB_Value_Team1 =',RGB_Value_Team1) 
   
   
    RGB_Value_Team2=list(int(hex_code_team2[i:i+2], 16) for i in (0, 2, 4))
    print('RGB_Value_Team2 =',RGB_Value_Team2)
    return RGB_Value_Team1,RGB_Value_Team2