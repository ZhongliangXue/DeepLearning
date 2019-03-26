#encoding:utf-8
import nibabel as nib
import numpy as np
from skimage.segmentation import random_walker
from scipy import ndimage

from YunPlatform.common import *

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
### ——————————————————————区域生长部分结束————————————————————————————

## ——————————派生ToolObject的实例———————————————————————————————————————
class RW_PET(ToolObject):
    ## 前端传递的参数:切片的序列号（是一个一维数组）
    @property
    def fg_params(self):

        return dict(
            index = dict(typ=np.ndarray,default=np.zeros(1),check=lambda  x:(x.min() >= 0, "输入的切片序号中存在小于0的值"))
        )

    @property
    def var_params(self):

        return dict(
            input_data=dict(typ=np.ndarray, default=np.zeros(1), check=lambda x: (x.min() >= 0, "输入数据中存在小于0的值")),
            # binarization_threshold=dict(typ=float, default=0.5, check=lambda x: (x >= 0, "阈值小于0"))
        )

    ## 传递的图像路径的参数
    @property
    def path_params(self):

        return dict(
        input_data = dict(typ=str, is_file=True,handler=lambda x: dict(array = sitk.GetArrayFromImage(x)))
        )

    def ker_func(self,**kwargs):
        data = nib.load(kwargs['input_data'])
        nii_array = data.get_data()

        print(nii_array.shape)

        ## 这块需要输出一个切片的信息，上海 方面  说他们在前端部分解决，所以还是当成index和input_data参数同时输入
        SUV_up = np.max(nii_array)
        high_seed = SUV_up * 0.5
        low_seed = SUV_up * 0.05

        ## 以第一张分割结果的切片为 存储路径，不断的将后面的二维矩阵合并到save_result中
        ## 得到的分割结果矩阵的存储顺序是 按照读入的顺序进行存储的
        save_result = np.ones(nii_array.shape)
        for i in range(0,len(kwargs['index'])):
            slice_array = nii_array[:,:,kwargs['index'][i]]
            slice_array = np.rot90(slice_array)
            slice_array = ndimage.zoom(slice_array,4,order=1)
            max_point = np.where(slice_array == np.max(slice_array))   ## 找到SUV值最大的一个像素点，作为区域生长的种子点；背景点默认为[0,0]了

            ## ————————————先对图片进行区域生长的处理，得到一个限制轮廓——————————————————
            seeds = [Point(0, 0), Point(max_point[0][0], max_point[1][0])]
            binaryImg = regionGrow(slice_array, seeds, 120)
            binaryImg[binaryImg == 0] = 2             ## 为了计算两个矩阵的点乘，label==4的区域就是预测的病灶区域了
            ## ————————————————区域生长结束——————————————————————————————

            markers = np.zeros(slice_array.shape, dtype=np.uint8)
            markers[slice_array > high_seed] = 2
            markers[slice_array < low_seed] = 1

            labels = random_walker(slice_array, markers, beta=200000, mode='bf')

            result = binaryImg * labels
            result[result < 4] = 0
            save_result[:,:,kwargs['index'][i]] = result

        return save_result

if __name__== '__main__':
    input_data = r'C:\Users\XML\Desktop\PET数据/P1.nii'
    index = [131,132,133]
    test = RW_PET.ker_func({index,input_data})
    test()
