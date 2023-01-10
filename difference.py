import os

import imagehash
import numpy as np
from PIL import Image

dirname = "grotto_images"
testdir = "test_images"
hash_size = 16

fnames = os.listdir(dirname)
tests = os.listdir(testdir)

for location in tests:
    with Image.open(os.path.join(testdir, location)) as img:
        hash1 = imagehash.average_hash(img, hash_size).hash

    smallest_diff = 100
    smallest_diff_image = ""
    smallest_diff_images = []
    for image in fnames:
        with Image.open(os.path.join(dirname, image)) as img:
            hash2 = imagehash.average_hash(img, hash_size).hash

            diff = np.count_nonzero(hash1 != hash2)

            if image == location.removeprefix("test"):
                print("Image: {} - Similarity: {}%".format(image, 100 - diff))

            if diff == smallest_diff:
                smallest_diff_images.append(image)
            elif diff < smallest_diff:
                smallest_diff = diff
                smallest_diff_image = image
                smallest_diff_images = [image]

    if len(smallest_diff_images) <= 1:
        print("{} image found {}% similar to {}".format(smallest_diff_image, 100 - smallest_diff, location))
        if smallest_diff_image == location.removeprefix("test"):
            print("Correct Image Found!")
    else:
        for image in smallest_diff_images:
            print("{} image found {}% similar to {}".format(image, 100 - smallest_diff, location))
            if image == location.removeprefix("test"):
                print("Correct Image Found!")
    print()
