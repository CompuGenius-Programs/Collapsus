import cv2
import os

import numpy as np

images_dir = "grotto_images"
images = os.listdir(images_dir)

image_features = []


# create a SIFT feature detector and descriptor
sift = cv2.xfeatures2d.SIFT_create()


# loop through each map image and match its features with the input image
for i, map_img_name in enumerate(images):
    # load the map image
    map_img = cv2.imread(images_dir + "/" + map_img_name)

    # detect and compute the features of the map image
    kp2, des2 = sift.detectAndCompute(map_img, None)
    image_features.append(des2)


def match_image(name):
    # create a brute-force matcher
    bf = cv2.BFMatcher()

    # convert io.bytesIO to file
    input_img = cv2.imdecode(np.frombuffer(name.getbuffer(), np.uint8), cv2.IMREAD_UNCHANGED)

    # load the input image
    # input_img = cv2.imread(img)

    # detect and compute the features of the input image
    kp1, des1 = sift.detectAndCompute(input_img, None)

    # initialize the minimum distance and closest map index
    min_dist = float('inf')
    closest_map_index = -1

    # loop through each map image and match its features with the input image
    for i, des2 in enumerate(image_features):
        # match the features between the two images
        matches = bf.match(des1, des2)

        # calculate the distance between the matched features
        dist = sum([m.distance for m in matches])

        # check if this map image is closer than the previous ones
        if dist < min_dist:
            min_dist = dist
            closest_map_index = i

    # print the closest map index
    image = images[closest_map_index + 1]
    print(f"The input image is closest to map {image}")
    return image


# import os
#
# images = os.listdir("grotto_images")
#
# locs = [
#     '01', '02', '03', '04',
#     '86', ' ', ' ', ' ',
#     '05', '06', '07', '08',
#     ' ', ' ', ' ', ' ',
#     '09', '0A', '0B', '87',
#     '88', ' ', ' ', ' ',
#     '0C', '0D', '0E', '0F',
#     '10', ' ', ' ', ' ',
#     '11', '12', '13', ' ',
#     ' ', ' ', ' ', ' ',
#     '14', '15', '16', '17',
#     '18', ' ', ' ', ' ',
#     '19', '1A', '1B', '1C',
#     '68', '89', '8A', ' ',
#     '1D', '1E', '1F', '20',
#     '21', '8B', '8C', ' ',
#     '22', '23', '24', ' ',
#     ' ', ' ', ' ', ' ',
#     '25', '26', '27', ' ',
#     ' ', ' ', ' ', ' ',
#     '28', '29', '2A', ' ',
#     ' ', ' ', ' ', ' ',
#     '2B', '2C', '2D', '2E',
#     '2F', ' ', ' ', ' ',
#     '30', '31', '32', '8D',
#     '8E', '8F', ' ', ' ',
#     '33', ' ', ' ', ' ',
#     ' ', ' ', ' ', ' ',
#     '34', '35', '36', '37',
#     '38', '39', '3A', '90',
#     '3B', '3C', '3D', '3E',
#     '91', ' ', ' ', ' ',
#     '3F', '40', '41', '42',
#     '43', ' ', ' ', ' ',
#     '44', '45', '46', '47',
#     '48', ' ', ' ', ' ',
#     '49', '4A', '4B', '92',
#     ' ', ' ', ' ', ' ',
#     '4C', '4D', '4E', '4F',
#     '50', '51', '52', ' ',
#     '53', '54', '55', '56',
#     '57', ' ', ' ', ' ',
#     '58', '59', '5A', '5B',
#     '5F', '60', '61', ' ',
#     '5C', '5D', '5E', ' ',
#     ' ', ' ', ' ', ' ',
#     '62', '63', '64', ' ',
#     ' ', ' ', ' ', ' ',
#     '65', '66', '67', '93',
#     ' ', ' ', ' ', ' ',
#     '69', '6A', '6B', '6C',
#     '94', ' ', ' ', ' ',
#     '6D', '6E', '6F', '70',
#     '71', '95', ' ', ' ',
#     '72', '73', ' ', ' ',
#     ' ', ' ', ' ', ' ',
#     '74', '75', '76', '77',
#     '7B', '7C', '96', ' ',
#     '78', '79', '7A', ' ',
#     ' ', ' ', ' ', ' ',
#     '7D', '7E', '7F', '80',
#     ' ', ' ', ' ', ' ',
#     '81', '82', '83', ' ',
#     ' ', ' ', ' ', ' ',
#     '84', '85', ' ', ' ',
#     ' ', ' ', ' ', ' '
# ]
#
# # arrange images in a list going by value of Y: imageXxY.png, then sort by X
# images.sort(key=lambda x: (int(x.split("x")[1].split(".")[0]), int(x.split("x")[0].split("e")[1])))
#
# for index, image in enumerate(images):
#     if locs[index] == ' ':
#         os.remove("grotto_images/" + image)
#     else:
#         os.rename("grotto_images/" + image, "grotto_images/" + locs[index] + ".png")
