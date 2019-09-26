import cv2
import numpy as np
import argparse
import sys
from utils import mean_blur, gaussian_blur, gaussian_noise, salt_pepper, psnr



def denoising(args):    
    noise_functions = {
        'gauss': gaussian_noise,
        'saltpep': salt_pepper
    }
    blur_functions = {
        'mean': mean_blur,
        'median': cv2.medianBlur
    }

    image = cv2.imread(args.input_image, 0)
    noisy = noise_functions[args.noise_type](image, args.noise_param)
    
    max_psnr = -1 * float('inf')
    best_dim, best_denoised = None, None
    for dim in range(3, 31, 2):
        denoised = blur_functions[args.kernel_type](noisy, dim)
        p = psnr(image, denoised)
        print(f'[*] Filter with kernel dimension: {dim}, PSNR: {p}')
        
        if p > max_psnr:
            max_psnr = p
            best_dim = dim
            best_denoised = denoised
    
    print(f'[*] Best kernel: Dimension: {best_dim}, PSNR: {max_psnr}')
    cv2.imshow('', np.hstack((image, noisy, best_denoised)))
    cv2.waitKey()



def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('input_image', type=str)
    parser.add_argument('noise_type', type=str, choices=('gauss', 'saltpep'))
    parser.add_argument('noise_param', type=float)
    parser.add_argument('kernel_type', type=str, choices=('mean', 'median'))
    parser.set_defaults(func=denoising)

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args()
    args.func(args)


if __name__=='__main__':
    main()
