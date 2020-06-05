from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000


def get_rgb_color_difference(color1_rgb, color2_rgb):
    
    color1_rgb = sRGBColor(color1_rgb[0],color1_rgb[1],color1_rgb[2])

    color2_rgb = sRGBColor(color2_rgb[0],color2_rgb[1],color2_rgb[2])
    
    #Convert from RGB to Lab Color Space
    color1_lab = convert_color(color1_rgb, LabColor)

    # Convert from RGB to Lab Color Space
    color2_lab = convert_color(color2_rgb, LabColor)
    
    # Find the color difference
    delta_e = delta_e_cie2000(color1_lab, color2_lab)
    delta_e =int(delta_e)
    print("The difference between the 2 color = ", delta_e)
    return delta_e
    
    
    
