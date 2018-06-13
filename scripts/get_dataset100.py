
import math
import os
import random
import sys
from multiprocessing.pool import ThreadPool
import urllib

import file_util
import pandas as pd

ds = pd.read_csv("../data/simplemaps-worldcities-basic.csv") 

# Heuristically select from DB cities likely to be on google maps
cities = ds[ds["pop"]>20000][ds.iso3.isin([
    "USA", "GBR", "FRA", "JAP", "POL", "AUS","ARG" ,"KOR"])].sample(100)[["city_ascii", "lat", "lng"]]
cities.city_ascii = cities.city_ascii.apply(lambda x: x.replace(" ", "_"))
cities = { city[0]: (city[1], city[2]) for city in cities.as_matrix()}


# radius of the Earth
R = 6378.1

# radius of images around center of city
IMAGE_RADIUS = 10

# number of images to download from each city
NUM_IMAGES_PER_CITY = 100

# size of failed-download image
FAILED_DOWNLOAD_IMAGE_SIZE = 3464

# place key in a file in the Geo-Localization directory 
# as the only text in the file on one line
KEY_FILEPATH = "/home/ashedko/Projects/UIR/im2gps/LittlePlaNet/api_key.key"
API_KEY = file_utils.load_key(KEY_FILEPATH)
GOOGLE_URL = ("http://maps.googleapis.com/maps/api/streetview?"
              "size=256x256&fov=120&pitch=10&key=" + API_KEY)
IMAGES_DIR = '../data/cities/'


def download_images_for_city(city, lat, lon):
    print('downloading images of {}'.format(city))
    num_imgs = 0
    misses = 0
    cur_directory = os.path.join(IMAGES_DIR, city)
    if not os.path.exists(cur_directory):
        os.makedirs(cur_directory)

    while num_imgs < NUM_IMAGES_PER_CITY:
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
        res = urllib.request.urlretrieve(url, filepath)

        # check if the downloaded image was invalid and if so remove it
        if os.path.isfile(filepath):
            size = os.path.getsize(filepath)
            if size == FAILED_DOWNLOAD_IMAGE_SIZE:
                os.remove(filepath)
                misses += 1
            else:
                num_imgs += 1

    print('invalid photo of {} downloaded {} times'.format(city, misses))
#    file_utils.upload_directory_to_aws(cur_directory)

def download_images():

    # download images for each city in a different thread
    num_threads = 8
    pool = ThreadPool(num_threads)
    for city, (lat, lon) in cities.items():
        pool.apply_async(download_images_for_city, (city, lat, lon))

    pool.close()
    pool.join()

if __name__ == '__main__':
    download_images()
