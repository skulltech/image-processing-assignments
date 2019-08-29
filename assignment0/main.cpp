#include "CImg.h"
#include <iostream>
#include <string>

using namespace std;
using namespace cimg_library;


int main(int argc, char *argv[]) {
    if (argc != 3) {
        cout << "[*] Usage instruction: $ DIAO input.jpg output.jpg" << endl;
        return 1;
    }

    CImg<unsigned char> image(argv[1]);
    CImg<unsigned char> avg(image.width(), image.height(), 1, 3);
    int rsum, gsum, bsum, color[3];

    for (int j = 0; j < image.height(); j++) {
        rsum = 0, gsum = 0, bsum = 0;
        for (int i = 0; i < image.width(); i++) {
            rsum = rsum + *image.data(i, j, 0, 0);
            gsum = gsum + *image.data(i, j, 0, 1);
            bsum = bsum + *image.data(i, j, 0, 2);
        }
        color[0] = rsum / image.width();
        color[1] = gsum / image.width();
        color[2] = bsum / image.width();
        for (int i = 0; i < image.width(); i++) {
            avg.draw_point(i, j, 0, color);
        }
    };

    avg.save(argv[2]);
    return 0;
}
