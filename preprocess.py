import cv2
import numpy as np


def load_image(path):
    return cv2.imread(path)


def save_image(path, image):
    cv2.imwrite(path, image)


# 1 Grayscale
def to_gray(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


# 2 Binary Threshold
def apply_threshold(img):
    gray = to_gray(img)
    _, th = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    return th


# 3 Adaptive Threshold
def adaptive_threshold(img):
    gray = to_gray(img)
    return cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )


# 4 Denoise
def denoise(img):
    gray = to_gray(img)
    return cv2.fastNlMeansDenoising(gray)


# 5 Resize
def resize_image(img):
    return cv2.resize(img, None, fx=2, fy=2)


# 6 Sharpen
def sharpen_image(img):
    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]])
    return cv2.filter2D(img, -1, kernel)