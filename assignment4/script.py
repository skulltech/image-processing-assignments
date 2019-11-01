import cv2
import argparse
import sys
import numpy as np
import os
import statistics
from skimage import measure


def display(image, caption='Display'):
    cv2.imshow(caption, image)
    cv2.waitKey(0)


def __deskew(image, verbose=False):
    monochrome = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(monochrome, 300, 400)

    lines = cv2.HoughLines(edges, 1, np.pi/180, 200)
    lines = sorted(lines[:, 0, :], key=lambda x: x[0], reverse=True)
    lines = lines[:10]

    cimage = image.copy()
    for rho, theta in lines:
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*rho
        y0 = b*rho
        x1 = int(np.around(x0 + 1000*(-b)))
        y1 = int(np.around(y0 + 1000*(a)))
        x2 = int(np.around(x0 - 1000*(-b)))
        y2 = int(np.around(y0 - 1000*(a)))
        cv2.line(cimage, (x1, y1), (x2, y2), (0, 255, 0), 2)
    if verbose:
        display(cimage)

    thetas = [90 - (x[1]*180/np.pi) for x in lines]
    md = statistics.median(thetas)
    thetas = [theta - 90 if theta - md > 30 else 90 - abs(theta) if md - theta > 30 else theta for theta in thetas]
    angle = sum(thetas) / len(thetas)

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, -1 * angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated


def deskew(image):
    image = cv2.imread(image)
    image = cv2.resize(image, (1000, 1000))
    display(image)
    deskewed = __deskew(image)
    display(deskewed)


def get_rectangles(thresh, image, mask, p1, p2, a1, a2):
    cnts, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    canvas = image.copy()
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4 and cv2.contourArea(approx) > p1 and cv2.contourArea(approx) < p1:
            (x, y, w, h) = cv2.boundingRect(approx)
            ar = w / float(h)
            if ar > a1 and ar < a2:
                cv2.rectangle(canvas, (x, y), (x+w, y+h), (0, 255, 0), 1)
                cv2.rectangle(mask, (x, y), (x+w, y+h), (255, 255, 255), -1)
    return canvas, mask


def cca(thresh, image, mask, p1, p2, a1, a2):
    labels = measure.label(thresh, neighbors=8, background=0)
    canvas = image.copy()
    for label in np.unique(labels):
        if label == 0:
            continue
        labelMask = np.zeros(thresh.shape, dtype='uint8')
        labelMask[labels == label] = 255
        numPixels = cv2.countNonZero(labelMask)
        if numPixels > p1 and numPixels < p2:
            cnts, hierarchy = cv2.findContours(labelMask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for c in cnts:
                (x, y, w, h) = cv2.boundingRect(c)
                ar = w / float(h)
                if ar > a1 and ar < a2:
                    cv2.rectangle(canvas, (x, y), (x+w, y+h), (0, 255, 0), 1)
                    cv2.rectangle(mask, (x, y), (x+w, y+h), (255, 255, 255), -1)
    return canvas, mask


def draw_contours(image, contours):
    canvas = image.copy()
    cv2.drawContours(canvas, contours, -1, (0, 255, 0), 1)
    display(canvas)


def __segment(image):
    kernel = np.ones((3, 3), np.uint8)
    monochrome = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mask = np.zeros(monochrome.shape, dtype='uint8')
    blurred = cv2.GaussianBlur(monochrome, (3, 3), 0)
    P1, P2, A1, A2 = 1000, 10000, 1.2, 5

    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 31, 1)
    canvas, mask = get_rectangles(thresh, image, mask, P1, P2, A1, A2)

    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
    canvas, mask = get_rectangles(opening, canvas, mask, P1, P2, A1, A2)

    gradient = cv2.morphologyEx(thresh, cv2.MORPH_GRADIENT, kernel, iterations=1)
    canvas, mask = get_rectangles(gradient, canvas, mask, P1, P2, A1, A2)

    canvas, mask = cca(thresh, canvas, mask, P1, P2, A1, A2)
    return canvas, mask


def segment(image):
    image = cv2.imread(image)
    image = cv2.resize(image, (1000, 1000))
    image = __deskew(image)
    display(image)
    canvas, mask = __segment(image)
    display(canvas)


def detect(image):
    image = cv2.imread(image)
    image = cv2.resize(image, (1000, 1000))
    image = __deskew(image)
    monochrome = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    display(image)

    blurred = cv2.GaussianBlur(monochrome, (3, 3), 0)
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 31, 40)
    # display(thresh)

    canvas, mask = __segment(image)
    roi = cv2.bitwise_and(thresh, mask)
    # display(roi)

    canvas, mask = cca(thresh, image, mask, 70, 200, 0.2, 5)
    display(canvas)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', type=str, choices=['deskew', 'segment', 'detect'], help='Action to perform on image')
    parser.add_argument('-i', '--image', type=str, help='Single input image')
    parser.add_argument('-a', '--all', type=str, help='Run on all images inside the given directory')

    actions = {
        'deskew': deskew,
        'segment': segment,
        'detect': detect
    }

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)
    args = vars(parser.parse_args())
    if args['all']:
        for subdir, dirs, files in os.walk('all-images/'):
            for file in files:
                filepath = subdir + os.sep + file
                if filepath.endswith('.jpg'):
                    print(filepath)
                    actions[args['action']](filepath)
    else:
        actions[args['action']](args['image'])


if __name__ == '__main__':
    main()
