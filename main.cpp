#include "CImg.h"
#include <iostream>
#include <string>
#include <algorithm>
#include "helpers.h"

using namespace std;
using namespace cimg_library;



int main(int argc, char *argv[]) {
    // args: hdrimage ldrimage
    // if (argc != 3) {
    //     cout << "[*] Usage instruction: $ tnmp hdrimage ldrimage" << endl;
    //     return 1;
    // }

    CImg<unsigned short int> image(argv[1]);
    // image.save("original.png");
    // auto corrected = gammaCorrection(image);
    // corrected.save("corrected.png");
    // image = CImg<unsigned short int>(argv[1]);
    // auto range = dynamicRange(corrected);
    // cout << range.first << " " << range.second << endl;
    auto logLuminance = LogLuminance();
    auto converted = logLuminance.convert(image);
    converted.save("converted.png");
    auto range = dynamicRange(converted);
    cout << range.first << " " << range.second << endl;
    auto restored = logLuminance.restore(converted);
    restored.save("restored.png");
    range = dynamicRange(restored);
    cout << range.first << " " << range.second << endl;
    return 0;
}
