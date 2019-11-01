import cv2
import argparse
import sys
import numpy as np
import os
import statistics
from skimage import measure



def display(image, caption='Display'):
    res = image.shape[:2]
    ratio = image.shape[0] / 1000
    cv2.imshow(caption, cv2.resize(image, (int(res[1] / ratio), int(res[0] / ratio))))
    cv2.waitKey(0)


def cca(image):
    labels = measure.label(image, neighbors=8, background=0)
    mask = np.zeros(image.shape, dtype='uint8')
    for label in np.unique(labels):
        if label == 0:
            continue
        labelMask = np.zeros(image.shape, dtype='uint8')
        labelMask[labels == label] = 255
        numPixels = cv2.countNonZero(labelMask)
        if numPixels > 300:
            mask = cv2.add(mask, labelMask)
    return mask


def get_rectangles(image):
    cnts, hierarchy = cv2.findContours(image, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    rectangles = []
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4 and cv2.contourArea(approx) > 300:
            (x, y, w, h) = cv2.boundingRect(approx)
            ar = w / float(h)
            if ar > 2.0 and ar < 3.0:
                rectangles.append(c)
    return rectangles


def draw_contours(image, contours):
    canvas = image.copy()
    cv2.drawContours(canvas, contours, -1, (0, 255, 0), 1)
    display(canvas)


def segment(input_image):
    image = cv2.imread(input_image)
    image = cv2.resize(image, (1000, 1000))
    kernel = np.ones((3, 3), np.uint8)
    monochrome = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    display(monochrome)

    blurred = cv2.GaussianBlur(monochrome, (3, 3), 0)
    display(blurred)
    
    edges = cv2.Canny(monochrome, 50, 200)
    dil = cv2.dilate(edges, kernel, iterations=1)

    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 31, 1)
    display(thresh)
    rects = get_rectangles(thresh)
    draw_contours(image, rects)

    # added = cv2.add(thresh, dilation)
    # display(added)
    # subd = cv2.subtract(added, edges)
    # display(subd)


    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
    display(opening)
    rects = get_rectangles(opening)
    draw_contours(image, rects)

    gradient = cv2.morphologyEx(thresh, cv2.MORPH_GRADIENT, kernel, iterations=1)
    display(gradient)
    rects = get_rectangles(gradient)
    draw_contours(image, rects)



    # ed = cv2.subtract(opening, dil)
    # display(ed)
    # cd = cca(ed)
    # display(cd)
    # cd = cv2.add(cd, edges)
    # display(cd)
    # cd = cca(cd)
    # display(cd)

    # rects = get_rectangles(cd)
    # draw_contours(image, rects)


    # mask = cca(thresh)
    # display(mask)

    # total_rects = []

    # rects = get_rectangles(mask)
    # draw_contours(image, rects)
    # total_rects += rects
    
    # mask = cv2.subtract(mask, edges)
    # display(mask)
    # rects = get_rectangles(mask)
    # draw_contours(image, rects)
    # total_rects += rects

    # mask = cv2.add(mask, edges)
    # display(mask)
    # rects = get_rectangles(mask)
    # draw_contours(image, rects)
    # total_rects += rects


    # rects = get_rectangles(opening)
    # draw_contours(image, rects)
    # total_rects += rects

    # draw_contours(image, total_rects)




def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', type=str)
    parser.add_argument('-i', '--image', type=str)
    parser.add_argument('-a', '--all', action='store_true', help='Run on all images')

    actions = {
        'segment': segment
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


if __name__=='__main__':
    main()
