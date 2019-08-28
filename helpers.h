#include "CImg.h"
#include <iostream>
#include <string>
#include <algorithm>

using namespace std;
using namespace cimg_library;


// Class used to get luminance from RGB and vice versa.
class Luminance { 
    public: 
    CImg<unsigned short> originalImage, luminanceImage;
    CImg<float> ratioImage;

    CImg<unsigned short> convert(CImg<unsigned short> image) {
        originalImage = image;
        luminanceImage = CImg<unsigned short>(originalImage.width(), originalImage.height(), 1, 1);
        ratioImage = CImg<float>(originalImage.width(), originalImage.height(), 1, 3);
        unsigned short lumnc[1];
        float ratio[3];

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

    CImg<unsigned short int> restore(CImg<unsigned short> image) {
        luminanceImage = image;
        CImg<unsigned short> restored(luminanceImage.width(), luminanceImage.height(), 1, 3);
        unsigned short colors[3];

        for (int j = 0; j < luminanceImage.height(); j++) {
            for (int i = 0; i < luminanceImage.width(); i++) {
                float luminance = *luminanceImage.data(i, j, 0, 0);
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
class LogLuminance { 
    public: 
    CImg<unsigned short int> hdrImage, llImage;
    CImg<float> ratioImage;

    CImg<unsigned short int> convert(CImg<unsigned int> image) {
        hdrImage = image;
        llImage = CImg<unsigned int>(hdrImage.width(), hdrImage.height(), 1, 1);
        ratioImage = CImg<float>(hdrImage.width(), hdrImage.height(), 1, 3);
        unsigned short logLumnc[1];
        float ratio[3];

        for (int j = 0; j < hdrImage.height(); j++) {
            for (int i = 0; i < hdrImage.width(); i++) {
                float luminance = *hdrImage.data(i, j, 0, 0)*0.299 + *hdrImage.data(i, j, 0, 1)*0.587 + *hdrImage.data(i, j, 0, 1)*0.114;
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

    CImg<unsigned short> restore(CImg<unsigned short> image) {
        llImage = image;
        CImg<unsigned short> restored(llImage.width(), llImage.height(), 1, 3);
        unsigned short colors[3];

        for (int j = 0; j < llImage.height(); j++) {
            for (int i = 0; i < llImage.width(); i++) {
                float luminance = exp(*llImage.data(i, j, 0, 0));
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
    T mx = 0, mn = 1000;
    for (int j = 0; j < image.height(); j++) {
        for (int i = 0; i < image.width(); i++) {
            for (int k = 0; k < image.spectrum(); k++) {
                // pair<T, T> mnmx = min({*image.data(i, j, 0, k), mn, mx});
                mn = min(*image.data(i, j, 0, k), mn);
                mx = max(*image.data(i, j, 0, k), mx);
            }
        }
    }
    return make_pair(mn, mx);
}

CImg<unsigned short> gammaCorrection(CImg<unsigned short int> image) {
    CImg<unsigned short> corrected(image.width(), image.height(), 1, image.spectrum());
    unsigned short int colors[image.spectrum()];

    for (int j = 0; j < image.height(); j++) {
        for (int i = 0; i < image.width(); i++) {
            for (int k = 0; k < image.spectrum(); k++) {
                int orig = *image.data(i, j, 0, k);
                double crct = pow(orig, (1/2.2));
                colors[k] = (int) (crct * 255);
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