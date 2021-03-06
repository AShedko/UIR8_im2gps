import math
import os
import random
import sys
from multiprocessing.pool import ThreadPool
import urllib
import requests
from io import BytesIO
from PIL import Image

import file_utils

cities = {
"Paris" : (48.8567,2.3508),
"London" : (51.5072,-0.1275),
"Barcelona" : (41.3833,2.1833),
"Moscow" : (55.7500,37.6167),
"Sydney" : (-33.8650,151.2094),
"Rio" : (-22.9068,-43.1729),
"NYC" : (40.7127,-74.0059),
"SanFran" : (37.7833,-122.4167),
"Detroit" : (42.3314,-83.0458),
"DC" : (38.9047,-77.0164)
}

# radius of the Earth
R = 6378.1 

# radius of images around center of city
IMAGE_RADIUS = 10 

# number of images to download from each city
NUM_IMAGES_PER_CITY = 200

# size of failed-download image
FAILED_DOWNLOAD_IMAGE_SIZE = 3464

# place key in a file in the Geo-Localization directory 
# as the only text in the file on one line
KEY_FILEPATH = "/home/ashedko/Projects/UIR/im2gps/LittlePlaNet/api_key.key"
API_KEY = file_utils.load_key(KEY_FILEPATH)
GOOGLE_URL = ("http://maps.googleapis.com/maps/api/streetview?"
              "size=256x256&fov=120&pitch=10&key=" + API_KEY)
IMAGES_DIR = '../data/alb_cities/'


def download_images_for_city(city, lat, lon):
    print('downloading images of {}'.format(city))
    num_imgs = 0
    misses = 0
    num_in_alb = 0

    cur_directory = os.path.join(IMAGES_DIR, city)
    if not os.path.exists(cur_directory):
        os.makedirs(cur_directory)

    while num_imgs < 100:
        req_num = random.randint(3,8)
        while num_in_alb < req_num:
            num_in_alb = 0
            # randomly select latitude and longitude in the city
            brng = math.radians(random.uniform(0, 360)) # bearing is 90 degrees converted to radians.
            d = random.uniform(0, IMAGE_RADIUS)
            lat_rad = math.radians(lat) # current lat point converted to radians
            lon_rad = math.radians(lon) # current long point converted to radians
            rand_lat = math.asin(math.sin(lat_rad)*math.cos(d/R) +
                                 math.cos(lat_rad)*math.sin(d/R)*math.cos(brng))
            rand_lon = lon_rad + math.atan2(math.sin(brng)*math.sin(d/R)*math.cos(lat_rad),
                                            math.cos(d/R)-math.sin(lat_rad)*math.sin(rand_lat))
            rand_lat = math.degrees(rand_lat)
            rand_lon = math.degrees(rand_lon)
        
            # download image
            filename = 'lat-{}-lon-{}.jpg'.format(round(rand_lat, 4), round(rand_lon, 4))
            filepath = os.path.join(cur_directory, filename)
            url = GOOGLE_URL + "&location=" + str(rand_lat) + ","+ str(rand_lon)+"&heading="+str(brng)
            
            response = requests.get(url)
            img = Image.open(BytesIO(response.content))

            # check if the downloaded image was invalid and if so remove it
            if img.size() == FAILED_DOWNLOAD_IMAGE_SIZE:
                misses += 1
            else:
                num_in_alb += 1

        num_imgs += 1
    print('invalid photo of {} downloaded {} times'.format(city, misses))
#    file_utils.upload_directory_to_aws(cur_directory)

def download_images(args):

    # download images for each city in a different thread
    args 
    num_threads = 8
    pool = ThreadPool(num_threads)
    for city, (lat, lon) in cities.items():
        pool.apply_async(download_images_for_city, (city, lat, lon))

    pool.close()
    pool.join()

if __name__ == '__main__':
    download_images(sys.argv)
