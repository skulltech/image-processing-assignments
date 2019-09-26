import cv2
import numpy as np



def gaussian_noise(image, sd=10):
    noise = np.random.normal(0, sd, image.shape)
    image = image + noise
    image = np.clip(image, 0, 255).astype(np.uint8)
    return image

def salt_pepper(image, thres=0.01):
    rand = np.random.rand(image.shape[0], image.shape[1])
    pepper = ((rand > thres) * 255).astype(np.uint8)
    salt = ((rand > 1 - thres) * 255).astype(np.uint8)
    image = np.clip(image, salt, None)
    image = np.clip(image, None, pepper)
    return image


def mean_blur(image, dim=5):
    kernel = np.ones((dim, dim)) / (dim * dim)
    convolved = cv2.filter2D(image, -1, kernel)
    return convolved

def gaussian_blur(image, dim=5):
    kernel = cv2.getGaussianKernel(dim, 0)
    kernel = np.dot(kernel, kernel.transpose())
    image = cv2.filter2D(image, -1, kernel)
    return image, kernel


def psnr(image1, image2):
    mse = np.sum(np.square(image1 - image2)) / (image1.shape[0] * image1.shape[1])
    psnr = (20 * np.log10(255)) - (10 * np.log10(mse))
    return psnr
