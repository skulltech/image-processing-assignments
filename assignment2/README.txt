Basic Denoising:
    For gaussian noise, mean filter works better than median filter, but the difference in their performance are not that great.
    Wheras for salt and pepper noise, mean filter fails horribly, but median filter almost perfectly restores the image.

    I tried both the filters with varying kernel dimensions, and in both the cases the PSNR peaks some specific kernel dimension; for smaller kernels as well as larger kernels the PSNR decreases. The size of the optimal kernel depends upon the severity of the noise, a larger kernel would be required for more severe noise.
    
    For example, with the barbara image:
        Salt and pepper noise on 4% of the pixels: median filter with kernel size 3x3 works best, with PSNR 33.26.
        Gaussian noise with standard deviation 15: mean filter with kernel size 3x3 works best, with PSNR 30.92.



Non Local Means:
    My non local means implementation ended up being very slow [a run of the algorithm takes over 20 mins], so I couldn't experiment much. 

    The results from a sample run has been included in the submission, of which:
        1. Output image: nlmeans_barbara.png
        2. Console of the sample run: nlmeans_run.txt
        3. Parameters: The image was added gaussian noise with standard deviation 20, and then non local means algorithm with the parameter h=3 was run on it. 



Weiner Filtering:
    I started out with blurring the image with PSF of diameter 10 and added gaussian noise of standard deviation 10.
    Then running weiner filter on it with:
        1. Constant spectrum value yielded best results at: k = 1900, PSNR = 28.50.
        2. The ground truth spectrum of the original image yielded PSNR = 28.08.
