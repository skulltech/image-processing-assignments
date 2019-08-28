#include "CImg.h"
#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <complex>
#include "helpers.h"

using namespace std;
using namespace cimg_library;


const int range = 8;
double scales[range];
const double alpha1 = 1 / (2 * sqrt(2));
const double alpha2 = 1.6 * alpha1;
const int kernelLength = 101;


CImg<double> convolution(CImg<double> image1, CImg<double> image2) {
    cout << "Here" << endl;
    CImgList<double> freqImage1 = image1.get_FFT();
    CImgList<double> freqImage2 = image2.get_FFT();
    
    cout << freqImage1.at(0).width() << " " << freqImage1.at(0).height() << endl;
    cout << freqImage2.at(0).width() << " " << freqImage2.at(0).height() << endl;
    // auto cimage1 = CImg<complex<double>>(freqImage1.at(0).width(), freqImage1.at(0).height(), 1, 1);
    // auto cimage2 = CImg<complex<double>>(freqImage2.at(0).width(), freqImage2.at(0).height(), 1, 1);
}

template <typename T>
CImg<T> centerSurround(CImg<T> image) {
    auto R1 = CImgList<double>(range, kernelLength, kernelLength, 1, 1);
    auto R2 = CImgList<double>(range, kernelLength, kernelLength, 1, 1);
    auto V1 = CImgList<double>(range, image.width(), image.height(), 1, 1);
    auto V2 = CImgList<double>(range, image.width(), image.height(), 1, 1);
    double val[1];
    int id, jd;
    int kernelMid = (int) kernelLength / 2;

    for (int k = 0; k < range; k++) {
        for (int j = 0; j < kernelLength; j++) {
            for (int i = 0; i < kernelLength; i++) {
                id = i - kernelMid, jd = j - kernelMid;
                val[0] = exp(-1 * (pow(id, 2) + pow(jd, 2)) / pow(alpha1 * scales[k], 2)) /  (M_PI * pow(alpha1 * scales[k], 2));
                R1.at(k).draw_point(i, j, 0, val);
                val[0] = exp(-1 * (pow(id, 2) + pow(jd, 2)) / pow(alpha2 * scales[k], 2)) /  (M_PI * pow(alpha2 * scales[k], 2));
                R2.at(k).draw_point(i, j, 0, val); 
            }
        }
    }
    convolution(image, R1.at(0));
    return image;
}

CImg<unsigned char> reinhard(CImg<unsigned char> hdrImage) {
    for (int i = 0; i < range; i++) { scales[i] = pow(1.6, i); }
    auto ret = centerSurround(hdrImage);
    return hdrImage;
}

int main(int argc, char *argv[]) {
    // cout << "Start" << endl;
    CImg<float> image(argv[1]);
    // cout << image.height() << " " << image.width() << endl;
    // displayImage(image);
    // auto ret = reinhard(image);
    const CImg<unsigned char> img = image.RGBtoYCbCr().channel(0).resize(256,256);
    cout << img.width() << " " << img.height() << " " << img.spectrum() << " " << img.depth() << endl;
    CImgList<float> F = img.get_FFT();
    cout << F.at(0).width() << " " << F.at(0).height() << " " << F.at(0).spectrum() << " " << F.at(0).depth() << endl;
    
    return 0;
}