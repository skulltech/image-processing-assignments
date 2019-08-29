#include "CImg.h"
#include <iostream>
#include <string>
#include <algorithm>
#include "helpers.h"

using namespace std;
using namespace cimg_library;


int main(int argc, char *argv[]) {
    CImg<double> image(argv[1]);
    auto linearlyScaled = linearScaling(image, 1);
    auto corrected = gammaCorrection(linearlyScaled);
    displayImage(linearlyScaled);
    displayImage(corrected);
    auto range = dynamicRange(corrected);
    cout << "[*] Dynamic Range: " << range.first << ", " << range.second << endl;
    return 0;
}
