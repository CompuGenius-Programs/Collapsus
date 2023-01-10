import os

import numpy as np
from PIL import Image
from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing import image

base_model = VGG16(weights='imagenet')
model = Model(inputs=base_model.input, outputs=base_model.get_layer('fc1').output)

images_dir = "grotto_images"
images = os.listdir(images_dir)

all_features = np.loadtxt("all_features.txt", delimiter=",")


def extract(img):
    img = img.resize((224, 224))  # Resize the image
    img = img.convert("RGB")  # Convert the image color space
    x = image.img_to_array(img)  # Reformat the image
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    feature = model.predict(x)[0]  # Extract Features
    return feature / np.linalg.norm(feature)


def match_image(name):
    img = Image.open(name)
    # img = img.convert("L")
    query = extract(img=img)  # Extract its features
    dists = np.linalg.norm(all_features - query, axis=1)  # Calculate the similarity (distance) between images
    id = np.argsort(dists)[0]  # Extract image that has the lowest distance

    return images[int(id)]

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
