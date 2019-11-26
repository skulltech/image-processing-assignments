import argparse
import os
import sys
import time

import cv2
import numpy as np
from PIL import Image


def gaussian_pyramid(image, levels):
    ims = [image]
    for l in range(levels - 1):
        blur = cv2.GaussianBlur(image, (5, 5), 0)
        im = np.zeros((blur.shape[0] // 2, blur.shape[1] // 2))
        for i in range(blur.shape[0] // 2):
            for j in range(blur.shape[1] // 2):
                im[i, j] = blur[i * 2, j * 2]
        ims.insert(0, im)
        image = im
    return ims


def neighborhood(g, l, nsizes, i, j):
    ns = []
    k = nsizes[l][1]
    i0, j0 = i, j

    for idx in range(k):
        i, j = i0 // pow(2, idx), j0 // pow(2, idx)
        image = g[l - idx]
        dim = nsizes[l - idx][0]
        d = (dim - 1) // 2
        image = cv2.copyMakeBorder(image, d, d, d, d, cv2.BORDER_WRAP)
        i = i + d
        j = j + d
        n = image[i - d:i + 1, j - d:j + d + 1]
        n = n.flatten()[:-(d + 1)]
        ns.append(n)

    return np.hstack(ns)


def nps(image):
    levels = 4
    nsizes = [(3, 1), (5, 2), (7, 2), (9, 2)]
    image = Image.open(image)
    image = np.array(image) / 255
    image = image[:128, :128]

    iia = image
    ga = gaussian_pyramid(iia, levels)
    iis = np.random.rand(image.shape[0], image.shape[1])
    gs = gaussian_pyramid(iis, levels)

    for l in range(levels):
        gai = ga[l]
        gsi = gs[l]
        start = time.time()
        print(l, gsi.shape)

        for xs in range(gsi.shape[0]):
            for ys in range(gsi.shape[1]):
                ns = neighborhood(gs, l, nsizes, xs, ys)
                c, match_best = None, -1 * float('inf')
                for xa in range(gai.shape[0]):
                    for ya in range(gai.shape[1]):
                        na = neighborhood(ga, l, nsizes, xa, ya)
                        match = np.sum(np.square(na - ns))
                        if match > match_best:
                            match_best = match
                            c = gai[xa, ya]
                gsi[xs, ys] = c
        print(f'[*] Time taken: {time.time() - start}')

    for l in range(levels):
        stacked = np.hstack((ga[l], gs[l]))
        cv2.imshow('Non-parametric Synthesis', stacked)
        cv2.imwrite(f'{l}.jpg', (stacked * 255).astype(np.uint8))
        cv2.waitKey(0)


def rpn(image):
    image = Image.open(image)
    image = np.array(image)

    random_phase = np.pi * (1 - 2 * np.random.rand(image.shape[0] // 2, image.shape[1]))
    random_phase = np.vstack((random_phase, -1 * random_phase))
    for idx in [(0, 0), (image.shape[0] // 2, 0), (0, image.shape[1] // 2), (image.shape[1] // 2, image.shape[1] // 2)]:
        random_phase[idx[0], idx[1]] = np.pi * np.random.randint(0, 1)
    radii = np.abs(np.fft.fft2(image))
    synthetic = radii * np.exp(1j * random_phase)
    synthetic = np.fft.ifft2(synthetic)
    synthetic = np.abs(synthetic).astype(np.uint8)
    stacked = np.hstack((image, synthetic))

    cv2.imshow('RPN Texture Synthesis', stacked)
    cv2.waitKey(0)
    return stacked


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', type=str, choices=['rpn', 'nps'], help='Action to perform on image')
    parser.add_argument('-i', '--image', type=str, help='Single input image')
    parser.add_argument('-a', '--all', type=str, help='Run on all images inside the given directory')

    actions = {
        'rpn': rpn,
        'nps': nps
    }

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)
    args = vars(parser.parse_args())
    if args['all']:
        for subdir, dirs, files in os.walk(args['all']):
            for file in files:
                filepath = os.path.join(subdir, file)
                if filepath.endswith('.jpg') or filepath.endswith('.gif'):
                    print(filepath)
                    output = actions[args['action']](filepath)
                    cv2.imwrite('output_' + filepath.split('/')[-1] + '.jpg', output)
    else:
        output = actions[args['action']](args['image'])
        cv2.imwrite('output_' + args['image'].split('/')[-1] + '.jpg', output)


if __name__ == '__main__':
    main()
