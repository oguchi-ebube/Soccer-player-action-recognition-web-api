from __future__ import print_function
from webapi import api
import binascii
import struct
import PIL
from PIL import Image
import numpy as np
import scipy
import scipy.misc
import scipy.cluster
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000


def get_dominant_color(img):
    print('reading image')
    
    # im = Image.fromarray(img)
    # # img = im.save(api.config["BASE_DIR"]+"/"+"api/static/human.png")
    im = Image.open(img)
    # # print("this is the image from the dominant colour:",img)
    
    im = im.resize((150, 150))      # optional, to reduce time
    ar = np.asarray(im)
    
    shape = ar.shape
    ar = ar.reshape(scipy.product(shape[:2]), shape[2]).astype(float)
    
    
    # print('finding clusters')
    codes, dist = scipy.cluster.vq.kmeans(ar, 10)
    
    print('cluster centres:\n', codes)
    
    
    vecs, dist = scipy.cluster.vq.vq(ar, codes)         # assign codes
    counts, bins = scipy.histogram(vecs, len(codes))    # count occurrences
    
    index_max = scipy.argmax(counts)                    # find most frequent
    peak = codes[index_max]
    
    print("These are the peaks:",peak)
    
    colour = binascii.hexlify(bytearray(int(c) for c in peak)).decode('ascii')
    print("This is the color:",colour)
    
    return peak 
    
    
