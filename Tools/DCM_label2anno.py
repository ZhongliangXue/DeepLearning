import SimpleITK as sitk
import matplotlib.image as mpimg
import numpy as np
from skimage.filters import roberts
from scipy import ndimage as ndi
import cv2

# 标注完全连续的处理情况，文字不存在矩形边框
def anno_process_continuity(anno_data):
    '''
    输入：anno标注数据，二维矩阵
    '''
    anno_data = np.array(anno_data,np.uint8)
    image,contours,hierarchy = cv2.findContours(anno_data, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    max_area = -1
    index = -1
    for i in range(len(contours)):
        if cv2.contourArea((contours[i])) > max_area:
            max_area = cv2.contourArea(contours[i])
            index = i
    # print(contours[index].shape)
    new_anno_data = np.zeros_like(anno_data)
    new_anno_data[contours[index][...,1],[contours[index][...,0]]] = 1
    edges = roberts(new_anno_data)
    new_anno_data = ndi.binary_fill_holes(edges).astype(np.uint8)
    #plt.imshow(new_anno_data)
    #plt.show()
    return new_anno_data

def anno_process_cut(anno_data):
    '''
    :param anno_data: 初步处理后的anno标注数据，非规则的二维矩阵
    :return: 裁剪后的，默认为512*512大小的矩阵：如果原始切片为1024*1024，可以使用其他工具放缩。
    '''
    imageHight = anno_data.shape[0]
    imageWidth = anno_data.shape[1]
    anno_data = anno_data[:,int((imageWidth - imageHight)/2):int(imageWidth - (imageWidth - imageHight)/2)]
    anno_data = ndi.zoom(anno_data, (512/imageHight, 512/imageHight), order=3)

    return anno_data

DICOM_path = r'C:\Users\XML\PycharmProjects\DeepLearning\Tools\151'
png_savepath_0 = r'C:\Users\XML\PycharmProjects\DeepLearning\Tools/158_0.png'
png_savepath_1 = r'C:\Users\XML\PycharmProjects\DeepLearning\Tools/158_1.png'

img = sitk.ReadImage(DICOM_path)
origin_array = sitk.GetArrayFromImage(img)

single_array = origin_array[0,:,:,:]

array_0 = single_array[:,:,0]
print(array_0.shape)
print(np.max(array_0), np.min(array_0))

index_x, index_y = np.where(array_0 != 0)

# 通过通道像素的选择，去除连接的一条白线、切片的序列号(红、黄色)
array_1 = single_array[:,:,1]
for i in range(0,index_x.shape[0]):
    array_1[index_x[i], index_y[i]] = 0

# 通过检查连通域，把图像中的文字部分去掉
array_1 = anno_process_continuity(array_1)
array_1 = anno_process_cut(array_1)

mpimg.imsave(png_savepath_1, array_1, cmap='gray')
mpimg.imsave(png_savepath_0, single_array)
