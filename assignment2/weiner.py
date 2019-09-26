import cv2
import numpy as np
import argparse
import sys
from utils import gaussian_noise, gaussian_blur, psnr



def weiner_filter(image, kernel, k):
    H = np.fft.fft2(kernel, s=image.shape)
    W = np.conj(H) / ((np.abs(H) ** 2) + k)
    Fcap = W * np.fft.fft2(image)
    fcap = np.abs(np.fft.ifft2(Fcap))
    return fcap.astype(np.uint8)


def driver(args):
    image = cv2.imread(args.input_image, 0)
    
    psf = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (args.psf_diam, args.psf_diam))
    psf = psf / np.sum(psf)
    degraded = cv2.filter2D(image, -1, psf)
    degraded = gaussian_noise(degraded, args.noise_sd)

    max_psnr = -1 * float('inf')
    optimal_k, best_restored = None, None
    for i in range(1, 101):
        k = 0.01 * i
        restored = weiner_filter(degraded, psf, k)
        p = psnr(image, restored)
        print(f'[*] k: {k}\tPSNR: {p}')
        
        if p > max_psnr:
            max_psnr = p
            optimal_k = k
            best_restored = restored

    print(f'[*] Optimal K: {optimal_k}, Max PSNR: {max_psnr}')
    cv2.imshow('', np.hstack((image, degraded, best_restored)))
    cv2.waitKey()


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('input_image', type=str)
    parser.add_argument('psf_diam', type=int)
    parser.add_argument('noise_sd', type=float)
    parser.set_defaults(func=driver)

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args()
    args.func(args)



if __name__=='__main__':
    main()
