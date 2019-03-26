import cv2
import matplotlib.image as mpimg
from scipy import misc

if __name__ == '__main__':
    #放大图像,宽和高都放大为4倍
    #INTER_NEAREST	最近邻插值;INTER_LINEAR	双线性插值（默认设置）
    #INTER_AREA	使用像素区域关系进行重采样。 它可能是图像抽取的首选方法，因为它会产生无云纹理的结果。 但是当图像缩放时，它类似于INTER_NEAREST方法。
    #INTER_CUBIC	4x4像素邻域的双三次插值
    #INTER_LANCZOS4	8x8像素邻域的Lanczos插值
    # CUBIC = cv2.resize(img,(901,1018),interpolation=cv2.INTER_CUBIC)
    # misc.imsave('./3.png',CUBIC)

#####——————————————————第二种放大方式——————————
    image = cv2.imread('./3.jpg')
    resized = cv2.resize(image,(901,1018),interpolation=cv2.INTER_AREA)
    cv2.imshow("resized", resized)
    cv2.waitKey(0)
    # cv2.imwrite('./33.jpg',resized)
