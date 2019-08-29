#include "CImg.h"
#include <iostream>
#include <string>
#include <algorithm>

using namespace std;
using namespace cimg_library;


// Class used to get luminance from RGB and vice versa.
template <typename T>
class Luminance { 
    public: 
    CImg<T> originalImage, luminanceImage;
    CImg<double> ratioImage;

    CImg<T> convert(CImg<T> image) {
        originalImage = image;
        luminanceImage = CImg<T>(originalImage.width(), originalImage.height(), 1, 1);
        ratioImage = CImg<double>(originalImage.width(), originalImage.height(), 1, 3);
        T lumnc[1];
        double ratio[3];

        for (int j = 0; j < originalImage.height(); j++) {
            for (int i = 0; i < originalImage.width(); i++) {
                lumnc[0] = *originalImage.data(i, j, 0, 0)*0.299 + *originalImage.data(i, j, 0, 1)*0.587 + *originalImage.data(i, j, 0, 1)*0.114;
                ratio[0] = *originalImage.data(i, j, 0, 0) / lumnc[0];
                ratio[1] = *originalImage.data(i, j, 0, 1) / lumnc[0];
                ratio[2] = *originalImage.data(i, j, 0, 2) / lumnc[0];
                luminanceImage.draw_point(i, j, 0, lumnc);
                ratioImage.draw_point(i, j, 0, ratio);
            }
        }
        return luminanceImage;
    }

    CImg<T> restore(CImg<T> image) {
        luminanceImage = image;
        CImg<T> restored(luminanceImage.width(), luminanceImage.height(), 1, 3);
        T colors[3];

        for (int j = 0; j < luminanceImage.height(); j++) {
            for (int i = 0; i < luminanceImage.width(); i++) {
                T luminance = *luminanceImage.data(i, j, 0, 0);
                colors[0] = *ratioImage.data(i, j, 0, 0) * luminance;
                colors[1] = *ratioImage.data(i, j, 0, 1) * luminance;
                colors[2] = *ratioImage.data(i, j, 0, 2) * luminance;
                restored.draw_point(i, j, 0, colors);
            }
        }
        return restored;
    }
};  


// class used to get logLuminance from RGB and vice versa.
template <typename T>
class LogLuminance { 
    public: 
    CImg<T> hdrImage, llImage;
    CImg<double> ratioImage;

    CImg<T> convert(CImg<T> image) {
        hdrImage = image;
        llImage = CImg<T>(hdrImage.width(), hdrImage.height(), 1, 1);
        ratioImage = CImg<double>(hdrImage.width(), hdrImage.height(), 1, 3);
        T logLumnc[1];
        double ratio[3];

        for (int j = 0; j < hdrImage.height(); j++) {
            for (int i = 0; i < hdrImage.width(); i++) {
                double luminance = *hdrImage.data(i, j, 0, 0)*0.299 + *hdrImage.data(i, j, 0, 1)*0.587 + *hdrImage.data(i, j, 0, 1)*0.114;
                logLumnc[0] = log(luminance);
                ratio[0] = *hdrImage.data(i, j, 0, 0) / luminance;
                ratio[1] = *hdrImage.data(i, j, 0, 1) / luminance;
                ratio[2] = *hdrImage.data(i, j, 0, 2) / luminance;
                llImage.draw_point(i, j, 0, logLumnc);
                ratioImage.draw_point(i, j, 0, ratio);
            }
        }
        return llImage;
    }

    CImg<T> restore(CImg<T> image) {
        llImage = image;
        CImg<T> restored(llImage.width(), llImage.height(), 1, 3);
        T colors[3];

        for (int j = 0; j < llImage.height(); j++) {
            for (int i = 0; i < llImage.width(); i++) {
                double luminance = exp(*llImage.data(i, j, 0, 0));
                colors[0] = *ratioImage.data(i, j, 0, 0) * luminance;
                colors[1] = *ratioImage.data(i, j, 0, 1) * luminance;
                colors[2] = *ratioImage.data(i, j, 0, 2) * luminance;
                restored.draw_point(i, j, 0, colors);
            }
        }
        return restored;
    }
};  


// Returns a pair containing the lowest value and highest value in the image.
template <typename T>
pair<T, T> dynamicRange(CImg<T> image) {
    double mx = -1 * INFINITY, mn = INFINITY;
    pair<T, T> mnmx;
    
    for (int j = 0; j < image.height(); j++) {
        for (int i = 0; i < image.width(); i++) {
            for (int k = 0; k < image.spectrum(); k++) {
                mnmx = minmax({*image.data(i, j, 0, k), mnmx.first, mnmx.second});
            }
        }
    }
    return mnmx;
}


// Gamma correction with gamma value of 2.2.
template <typename T>
CImg<T> gammaCorrection(CImg<T> image) {
    CImg<T> corrected(image.width(), image.height(), 1, image.spectrum());
    T colors[image.spectrum()];

    for (int j = 0; j < image.height(); j++) {
        for (int i = 0; i < image.width(); i++) {
            for (int k = 0; k < image.spectrum(); k++) {
                T orig = *image.data(i, j, 0, k);
                double crct = pow(orig, (1/2.2));
                colors[k] = (T) (crct * 255);
            }
            corrected.draw_point(i, j, 0, colors);
        }
    }
    return corrected;
}


// Linearly scales a given image containing a single channel in a given range.
template <typename T>
CImg<double> linearScaling(CImg<T> image, int range) {
    CImg<double> scaled = CImg<double>(image.width(), image.height(), 1, 1);
    double pixel[1];
    auto drange = dynamicRange(image);

    for (int j = 0; j < image.height(); j++) {
        for (int i = 0; i < image.width(); i++) {
            double val = (*image.data(i, j, 0, 0) - drange.first) * ((double) range / (drange.second - drange.first));
            // cout << val << endl;
            pixel[0] = val;
            scaled.draw_point(i, j, 0, pixel);
        }
    } 
    return scaled;
}


// Takes luminance image and returns log-average luminance as defined in Reinhard Et Al.
template <typename T>
double logAverageLuminance(CImg<T> image) {
    double delta = 0.00001, logSum = 0; 

    for (int j = 0; j < image.height(); j++) {
        for (int i = 0; i < image.width(); i++) {
            logSum = logSum + log(delta + *image.data(i, j, 0, 0));
        }
    }
    int pixelCount = image.height() * image.width();
    return exp(logSum / pixelCount);;
}


// Displays an image and waits till the window is closed by user.
template <typename T>
void displayImage(CImg<T> image) {
    auto display = CImgDisplay(image, "Image");
    while (!display.is_closed()) {
        display.wait();
    }
}
