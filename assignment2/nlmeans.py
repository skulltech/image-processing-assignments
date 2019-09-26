import cv2
import numpy as np
import time
import argparse
import sys
from utils import gaussian_noise, salt_pepper, mean_blur


def non_local_means(image, h):
    mean = mean_blur(image)
    weighting_function = lambda p, q: np.exp(-1 * np.square((p - q) / h))
    processed = np.ndarray(image.shape)

    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            print('[*] Processing pixel:', i, j)
            weights = weighting_function(image, image[i, j])
            pixel = np.sum(image * weights) / np.sum(weights)
            processed[i, j] = pixel
    return processed


def driver(args):
    start = time.time()
    noise_functions = {
        'gauss': gaussian_noise,
        'saltpep': salt_pepper
    }
    
    image = cv2.imread(args.input_image, 0)
    noisy = noise_functions[args.noise_type](image, args.noise_param)
    denoised = non_local_means(image, args.h)
    cv2.imwrite('nlmeans_'+ args.input_image.split('/')[-1], np.hstack((image, noisy, denoised)))

    print('[*] Time elapsed:', time.time() - start)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('input_image', type=str)
    parser.add_argument('noise_type', type=str, choices=('gauss', 'saltpep'))
    parser.add_argument('noise_param', type=float)
    parser.add_argument('h', type=float)
    parser.set_defaults(func=driver)

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args()
    args.func(args)



if __name__=='__main__':
    main()
