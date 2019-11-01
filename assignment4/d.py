
def weird(image):
    mask = image
    height,width = mask.shape
    skel = np.zeros([height,width],dtype=np.uint8)      #[height,width,3]
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3))
    temp_nonzero = np.count_nonzero(mask)
    while(np.count_nonzero(mask) != 0 ):
        eroded = cv2.erode(mask,kernel)
        # cv2.imshow("eroded",eroded)   
        temp = cv2.dilate(eroded,kernel)
        # cv2.imshow("dilate",temp)
        temp = cv2.subtract(mask,temp)
        skel = cv2.bitwise_or(skel,temp)
        mask = eroded.copy()
    display(skel)