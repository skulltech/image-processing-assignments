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


def deskew(input_image):
    image = cv2.imread(input_image)
    image = cv2.resize(image, (1000, 1000))
    display(image)
    monochrome = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # display(monochrome)

    edges = cv2.Canny(monochrome, 300, 400)
    # display(edges)

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
    display(cimage)

    thetas = [90 - (x[1]*180/np.pi) for x in lines]
    print(thetas)
    md = statistics.median(thetas)
    print(md)

    thetas = [theta - 90 if theta - md > 30 else 90 - abs(theta) if md - theta > 30 else theta for theta in thetas]
    print(thetas)

    angle = sum(thetas) / len(thetas)

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, -1 * angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    display(rotated)


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
    cnts, hierarchy = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # cnts, hierarchy = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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


def get_mask(image, contours):
    canvas = image.copy()
    # cv2.fillPoly(canvas, pts=contours, color=(255, 255, 255))
    for c in contours:
        cv2.drawContours(canvas, [c], -1, (255, 255, 255), cv2.FILLED)
    return canvas


def segment(input_image):
    image = cv2.imread(input_image)
    image = cv2.resize(image, (1000, 1000))
    kernel = np.ones((3, 3), np.uint8)
    monochrome = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    display(monochrome)

    blurred = cv2.GaussianBlur(monochrome, (3, 3), 0)
    # display(blurred)
    
    edges = cv2.Canny(monochrome, 50, 200)
    dil = cv2.dilate(edges, kernel, iterations=1)

    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 31, 1)
    # display(thresh)
    rects = get_rectangles(thresh)
    # draw_contours(image, rects)
    mask = get_mask(monochrome, rects)
    # display(mask)

    # added = cv2.add(thresh, dil)
    # display(added)
    # subd = cv2.subtract(added, edges)
    # display(subd)

    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
    # display(opening)
    rects = get_rectangles(opening)
    # draw_contours(image, rects)
    mask = get_mask(mask, rects)
    # display(mask)

    gradient = cv2.morphologyEx(thresh, cv2.MORPH_GRADIENT, kernel, iterations=1)
    # display(gradient)
    rects = get_rectangles(gradient)
    # draw_contours(image, rects)
    mask = get_mask(mask, rects)
    # display(mask)

    # Done, next experiment

    ed = cv2.subtract(opening, dil)
    # display(ed)
    rects = get_rectangles(gradient)
    # draw_contours(image, rects)
    mask = get_mask(mask, rects)
    # display(mask)
    cd = cca(ed)
    # display(cd)
    rects = get_rectangles(gradient)
    # draw_contours(image, rects)
    mask = get_mask(mask, rects)
    # display(mask)
    cd = cv2.add(cd, edges)
    # display(cd)
    rects = get_rectangles(gradient)
    # draw_contours(image, rects)
    mask = get_mask(mask, rects)
    # display(mask)
    cd = cca(cd)
    # display(cd)
    rects = get_rectangles(gradient)
    # draw_contours(image, rects)
    mask = get_mask(mask, rects)
    display(mask)



def detect(image):
    image = cv2.imread(image)
    image = cv2.resize(image, (1000, 1000))
    kernel = np.ones((3, 3), np.uint8)
    monochrome = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    display(monochrome)

    blurred = cv2.GaussianBlur(monochrome, (3, 3), 0)
    
    edges = cv2.Canny(monochrome, 50, 200)
    dil = cv2.dilate(edges, kernel, iterations=1)

    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 31, 1)
    display(thresh)
    # thresh = cv2.bitwise_not(thresh)
    # display(thresh)
    # thresh = cv2.subtract(thresh, edges)
    # display(thresh)
    
    labels = measure.label(thresh, neighbors=8, background=0)
    mask = np.zeros(thresh.shape, dtype='uint8')
    for label in np.unique(labels):
        if label == 0:
            continue
        labelMask = np.zeros(thresh.shape, dtype='uint8')
        labelMask[labels == label] = 255
        numPixels = cv2.countNonZero(labelMask)
        # if numPixels > 80 and numPixels < 300:
        if numPixels > 300:
            mask = cv2.add(mask, labelMask)
            cnts, hierarchy = cv2.findContours(labelMask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for c in cnts:
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(image,(x,y),(x+w,y+h),(0,255,0), 1)
    display(mask)
    display(image)
    


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', type=str)
    parser.add_argument('-i', '--image', type=str)
    parser.add_argument('-a', '--all', action='store_true', help='Run on all images')

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


if __name__=='__main__':
    main()
