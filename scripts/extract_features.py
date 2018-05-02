import torch
import torchvision
import numpy as np
import os
import sys

model_prototxt = '../features/deploy.prototxt'
model_trained = '../models/best_citynet/_iter_100000.caffemodel'
mean_path = '../data/cities/mean_image.binaryproto'
layer_name = 'pool5/7x7_s1'
image_list_filepath = '../data/cities/train.txt'
features_filepath = '../features/features.txt'
labels_filepath = '../features/label.txt'
image_filepaths = '../features/image_filepaths.txt'

DATA_PATH = "../data/cities/"

def crop_center(img):
    return img[16:-16,16:-16,:]

def main():

    blob = caffe.proto.caffe_pb2.BlobProto()
    data = open(mean_path, 'rb').read()
    blob.ParseFromString(data)
    arr = np.array(caffe.io.blobproto_to_array(blob))
    mean = arr[0][:,16:-16,16:-16]

    net = caffe.Classifier(model_prototxt, model_trained,
                          mean=mean,
                          channel_swap=(2,1,0),
                          raw_scale=255,
                          image_dims=(256, 256))


    labels = []
    filepaths =[]
    count = 0
    with open(image_list_filepath, 'r') as reader:
        with open(features_filepath, 'w') as fw:
            for line in reader:
                count += 1
                if count > 1000:
                    break
                image_path, label = line.strip().split(' ')
                image_path = DATA_PATH + image_path
                labels.append(label)
                filepaths.append(image_path)
                print('extracting from: {}'.format(image_path))
                input_image = crop_center(caffe.io.load_image(image_path))
                prediction = net.predict([input_image], oversample=False)
                np.savetxt(fw, net.blobs[layer_name].data[0].reshape(1,-1), fmt='%.5g')

    with open(labels_filepath, 'w') as writer:
        for label in labels:
            writer.write(label)
            writer.write('\n')

    with open(image_filepaths, 'w') as writer:
        for filepath in filepaths:
            writer.write(filepath)
            writer.write('\n')

if __name__ == "__main__":
    main()
