#encoding:utf-8
import nibabel as nib
import numpy as np
from skimage.segmentation import random_walker
from scipy import ndimage,misc
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from PIL import Image
import cv2

## ——————————————————————区域生长部分———————————————————————————————
class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def getX(self):
        return self.x

    def getY(self):
        return self.y

def getGrayDiff(img, currentPoint, tmpPoint):
    return abs(int(img[currentPoint.x, currentPoint.y]) - int(img[tmpPoint.x, tmpPoint.y]))

def selectConnects(p):
    if p != 0:
        connects = [Point(-1, -1), Point(0, -1), Point(1, -1), Point(1, 0), Point(1, 1), \
                    Point(0, 1), Point(-1, 1), Point(-1, 0)]
    else:
        connects = [Point(0, -1), Point(1, 0), Point(0, 1), Point(-1, 0)]
    return connects

def regionGrow(img, seeds, thresh, p=1):
    height, weight = img.shape
    seedMark = np.zeros(img.shape)
    seedList = []
    for seed in seeds:
        seedList.append(seed)
    label = 1
    connects = selectConnects(p)
    while (len(seedList) > 0):
        currentPoint = seedList.pop(0)

        seedMark[currentPoint.x, currentPoint.y] = label
        for i in range(8):
            tmpX = currentPoint.x + connects[i].x
            tmpY = currentPoint.y + connects[i].y
            if tmpX < 0 or tmpY < 0 or tmpX >= height or tmpY >= weight:
                continue
            grayDiff = getGrayDiff(img, currentPoint, Point(tmpX, tmpY))
            if grayDiff < thresh and seedMark[tmpX, tmpY] == 0:
                seedMark[tmpX, tmpY] = label
                seedList.append(Point(tmpX, tmpY))
    return seedMark
### ——————————————————————区域生长部分结束——————————————————————————————


## http://scikit-image.org/docs/dev/api/skimage.segmentation.html#skimage.segmentation.random_walker
def RW_on_PET_based_RG(nii_path,index):
    data = nib.load(nii_path)
    nii_array = data.get_data()
    # print('切片的总数量为：',nii_array.shape[2])
    SUV_up = np.max(nii_array)
    high_seed = SUV_up * 0.5
    low_seed = SUV_up * 0.05

    ###一次读入所有的nii数据且进行处理，但是一次只对对一张切片进行RW分割
    slice_array = nii_array[:,:,index]
    slice_array = np.rot90(slice_array)
    slice_array = ndimage.zoom(slice_array,4,order=1)
    max_point = np.where(slice_array == np.max(slice_array))

## ——————————————————先对图片进行区域生长处理，得到一个限制轮廓————————————————————
    seeds = [Point(0, 0), Point(max_point[0][0], max_point[1][0])]
    binaryImg = regionGrow(slice_array, seeds, 120)
    binaryImg[binaryImg == 0] = 2
    # print(np.max(binaryImg),np.min(binaryImg))
    # cv2.imshow(' ', binaryImg)
    # cv2.waitKey(0)
#————————————————————区域生长结束——————————————————————————————————

    markers = np.zeros(slice_array.shape,dtype=np.uint8)
    markers[slice_array > high_seed] = 2
    markers[slice_array < low_seed] = 1

    labels = random_walker(slice_array,markers,beta=200000,mode='bf')

    result = binaryImg * labels
    result[result < 4] = 0
    print(result)
   # # 绘制原图,种子图像和分割的图像
   #  print(nii_array.shape[0],nii_array.shape[1],nii_array.shape[2])
    # print(result)
   #  plt.imshow(result)
   #  plt.axis('off')
   #  plt.show()
    return result

if __name__=='__main__':
    nii_path = r'C:\Users\XML\Desktop\PET数据/P1.nii'
    index = 131
    max = np.max(RW_on_PET_based_RG(nii_path,index))
    min = np.min(RW_on_PET_based_RG(nii_path,index))



