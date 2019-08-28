#include "CImg.h"
#include <iostream>
#include <string>
#include <algorithm>
#include "helpers.h"

using namespace std;
using namespace cimg_library;


const int range = 8;
double scales[range];


CImg<double> centerSurround(CImg<unsigned char> image) {
    auto R1 = CImg<double>(image.height(), image.width(), range, 1);
    auto R2 = CImg<double>(image.height(), image.width(), range, 1);
    auto V1 = CImg<double>(image.height(), image.width(), range, 1);
    auto V2 = CImg<double>(image.height(), image.width(), range, 1);

    for (int j = 0; j < image.height(); j++) {
        for (int i = 0; i < image.width(); i++) {
            for (int k = 0; k < range; k++) {
                
            }
        }
    } }

CImg<unsigned char> reinhard(CImg<unsigned char> hdrImage) {
    for (int i = 0; i < range; i++) { scales[i] = pow(1.6, i); }

}

int main(int argc, char *argv[]) {
    CImg<unsigned short> image(argv[1]);
    auto lmnc = Luminance();
    auto limage = lmnc.convert(image);
    // auto scaled = linearScaling(limage, 6);

    auto drange1 = dynamicRange(image);
    cout << drange1.first << " " << drange1.second << endl;
    
    // auto drange2 = dynamicRange(scaled);
    // cout << (int) drange2.first << " " << (int) drange2.second << endl;
    

    // cout << image.width() << " " << image.width() << endl;
    double lalmnc = logAverageLuminance(image);
    // CImgDisplay displayImage(image, "HDR Input Image");
    cout << lalmnc << endl;
}