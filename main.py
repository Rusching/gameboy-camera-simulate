import cv2
import numpy as np
import shutil
import os

GBF_BYTES_PER_PIXEL = 4
GBF_BITS_PER_COMPONENT = 8
GBF_PIXELATE_DEFAULT_VALUE = 5

def getGreyscaleForValue(v):
    if v < 85: return 0
    elif v < 170: return 85
    elif v < 255: return 170
    else: return 255

def getMatrixFactorFromMatrixValue(v, mSize):
    return ((1.0+v)/(1.0+mSize))

OFFSET_MATRIX = [
    0, 48, 12, 60, 3, 51, 15, 63,
    32, 16, 44, 28, 35, 19, 47, 31,
    8, 56, 4, 52, 11, 59, 7, 55,
    40, 24, 36, 20, 43, 27, 39, 23,
    2, 50, 14, 62, 1, 49, 13, 61,
    34, 18, 46, 30, 33, 17, 45, 29,
    10, 58, 6, 54, 9, 57, 5, 53,
    42, 26, 38, 22, 41, 25, 37, 21
    ]

OFFSET_MATRIX_SIZE = 64

def filter_grey(image, height, width):
    filtered_image = np.zeros((height, width, 3))
    for r in range(height):
        for c in range(width):
            currentFactor = getMatrixFactorFromMatrixValue(OFFSET_MATRIX[(c & 7) + ((r & 7) << 3)], OFFSET_MATRIX_SIZE);
            currentGrey = (int(image[r][c][0]) + int(image[r][c][1]) + int(image[r][c][2])) * 0.33333;
            color = getGreyscaleForValue(currentGrey + currentFactor * 64);
            filtered_image[r][c][0] = 90
            filtered_image[r][c][1] = color
            filtered_image[r][c][2] = color
    return filtered_image

def filter_color(image, height, width):
    filtered_image = np.zeros((height, width, 3))
    for r in range(height):
        for c in range(width):
            currentFactor = getMatrixFactorFromMatrixValue(OFFSET_MATRIX[(c & 7) + ((r & 7) << 3)], OFFSET_MATRIX_SIZE);
            filtered_image[r][c][0] = getGreyscaleForValue(image[r][c][0] + currentFactor * 64)
            filtered_image[r][c][1] = getGreyscaleForValue(image[r][c][1] + currentFactor * 64)
            filtered_image[r][c][2] = getGreyscaleForValue(image[r][c][2] + currentFactor * 64)
    return filtered_image


def resize_image(image, height):
    # resize image to make he height is 128 pixels
    fixed_height = height
    curHight, curWidth, _ = image.shape
    resized_width = int(fixed_height * curWidth / curHight)
    resized_image = cv2.resize(image, dsize=(resized_width, fixed_height))
    return resized_image

def amplify_render(image, times):
    preHeight, preWidth, _ = image.shape
    amplifiedHeight, amplifiedWidth = preHeight * times, preWidth * times
    amplified_image = np.zeros((amplifiedHeight, amplifiedWidth, 3))
    for r in range(amplifiedHeight):
        for c in range(amplifiedWidth):
            preR = r // times
            preC = c // times
            amplified_image[r][c][0] = image[preR][preC][0]
            amplified_image[r][c][1] = image[preR][preC][1]
            amplified_image[r][c][2] = image[preR][preC][2]
    return amplified_image

def convert(inpath, outpath):
    test_image = cv2.imread(inpath)
    resized_image = resize_image(test_image, 128) # 84
    height, width, _ = resized_image.shape
    filtered_image = filter_grey(resized_image, height, width)
    amplifyed_image = amplify_render(filtered_image, 5)
    cv2.imwrite(outpath, amplifyed_image)
    
def main():
    base_dir = "./run"
    bak_dir = "./bak"
    image_list = os.listdir(base_dir)
    for each_image in image_list:
        input_path = os.path.join(base_dir, each_image)
        output_name = os.path.splitext(each_image)[0] + "_filtered.jpg"
        output_path = os.path.join(bak_dir, output_name)
        convert(input_path, output_path)
        # shutil.move(input_path, os.path.join(bak_dir, each_image))


main()

