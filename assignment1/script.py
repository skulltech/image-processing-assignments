import cv2
import numpy as np
import matplotlib.pyplot as plt


def div(a, b):
    with np.errstate(divide='ignore', invalid='ignore'):
        c = np.true_divide(a, b)
        c[~ np.isfinite(c)] = 0
    return c


class Luminance:
    def __init__(self):
        self.ratios = None
        self.color_image = None
        self.luminance_image = None

    def convert(self, image, log=False):
        self.color_image = image
        self.luminance_image = 0.299 * image[:, :, 0] + 0.587 * image[:, :, 1] + 0.114 * image[:, :, 2]
        self.ratios = np.stack((div(image[:, :, 0], self.luminance_image), div(image[:, :, 1], self.luminance_image), div(image[:, :, 2], self.luminance_image)), axis=-1)
        if log:
            self.luminance_image = np.log(self.luminance_image)
        return self.luminance_image
    
    def restore(self, image, log=False):
        if log:
            image = np.exp(image)
        restored = np.stack((image * self.ratios[:, :, 0], image * self.ratios[:, :, 1], image * self.ratios[:, :, 2]), axis=-1)        
        return restored


def logarithmic_scaling(image):
    lmnc = Luminance()
    luminance = lmnc.convert(image, log=True)
    mn = np.amin(luminance)
    mx = np.amax(luminance)
    scaling = lambda x: (x - mn) / (mx - mn)
    scaled = scaling(luminance)
    return lmnc.restore(scaled, log=True)


def linear_scaling(image):
    lmnc = Luminance()
    luminance = lmnc.convert(image)
    mn = np.amin(luminance)
    mx = np.amax(luminance)
    scaling = lambda x: (x - mn) / (mx - mn)
    scaled = scaling(luminance)
    return lmnc.restore(scaled)


image = cv2.imread('images/memorial.hdr', 0)
equ = cv2.equalizeHist(image)
res = np.hstack((image, equ))
cv2.imshow('', res)
cv2.waitKey()