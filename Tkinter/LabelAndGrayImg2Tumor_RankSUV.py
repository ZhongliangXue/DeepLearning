import numpy as np
import matplotlib.image as mpimg
from scipy import misc
import nibabel as nib
import os
import cv2
from PIL import Image

##获取原始DICOM矩阵的值，对SUV值进行截断处理。放大为512*512的矩阵
##用于计算后面的平均SUV值来保存病变区域
data = nib.load(r'C:\Users\XML\Desktop\PET/P2.nii')
nii_array = data.get_data()
nii_array = np.array(nii_array,float)
max_SUV = np.max(nii_array)
##阈值化的上限值(阈值化操作)
Up_res = 0.25*max_SUV
nii_array[nii_array > Up_res] = Up_res

file_object = open(r'C:\Users\XML\PycharmProjects\DeepLearning\Tkinter\test/myfile.txt')
file_content = file_object.read()
xx = int(file_content)

result_label_img_path = r'C:\Users\XML\PycharmProjects\DeepLearning\Tkinter\test\used_image/result_label_img_{}.bmp'.format(xx)
result_PET1_path = r'C:\Users\XML\PycharmProjects\DeepLearning\Tkinter\test\used_image/result_PET1_{}.bmp'.format(xx)

result_label_image = mpimg.imread(result_label_img_path)        #获取label(1-200)的label 矩阵
seg_PET1_image = mpimg.imread(result_PET1_path)                 #获取分割图像的矩阵

SUV_array = nii_array[:,:,xx]
SUV_array = np.rot90(SUV_array,1)
SUV_array = cv2.resize(SUV_array,(512,512),interpolation=cv2.INTER_CUBIC)
SUV_array = SUV_array[128:384,128:384]
SUV_array[SUV_array < 0] = 0

max_label = np.max(result_label_image)                 #获取lab的最大值，就是超像素的数量
count_label = np.zeros(max_label+1)                   #保存每个label的像素的数目
sum_SUV = np.zeros(max_label+1)                      #保存每个label的超像素的灰度值的和
mean_SUV = np.zeros(max_label+1)                     #创建一个数组，保存每个超像素的灰度值的均值(多了一个元)
##获取1-max_label的标签的对应的元素的坐标：在512*512的矩阵中找
##得到的x[i],y[i]为对应了label == i 的元的横坐标和纵坐标
for ii in range(1,(max_label+1)):
    bool_label_img = (result_label_image == ii)
    count_label[ii] = np.count_nonzero(bool_label_img)  #得到label=i的元素的数量,统计结果存储到一维数组中
    ##得到每个label的全部元素的SUV值的和
    [x,y] = np.where(result_label_image == ii)          #得到的x,y分别为两个一维矩阵，（x[j],y[j]）为第j个label值=i的元素的横纵坐标
    sum_SUV[ii] = 0
    for j in range(0,len(x)):
        sum_SUV[ii] = sum_SUV[ii] + SUV_array[x[j],y[j]]

    mean_SUV[ii] = sum_SUV[ii]/count_label[ii]         ##得到每个超像素的平均SUV值

###——————————————————保存一个病变可能性最大的区域————————————————————————
# ##得到SUV(平均)的最大值，得到对应的label,得到这个label的全部元素的坐标。显示这个区域：
SUV_aver_max = np.max(mean_SUV)
index_label = np.where(mean_SUV == SUV_aver_max)
index_label = list(index_label)
index_label = index_label[0]
##显示这个最大平均SUV值的区域
Tumor_image = (result_label_image == index_label)     #只有label值为index_label的值被保存，得到的是一个布尔矩阵。布尔矩阵与seg图像对应元相乘
Tumor_image = Tumor_image * seg_PET1_image
Tumor_image[Tumor_image == 0] = 255                    #将背景转化为白色
misc.imsave(r'C:\Users\XML\PycharmProjects\DeepLearning\Tkinter\test/TumorMP-{}.png'.format(xx),Tumor_image)

####——————————————————将SUV（max）*0.9  到 SUV(max)的区域保存出来
file_object2 = open(r'C:\Users\XML\PycharmProjects\DeepLearning\Tkinter\test/selection.txt')
file_content_selection = file_object2.read()
file_content_selection = int(file_content_selection)
index_sec_added_label = np.where(mean_SUV > (SUV_aver_max * (100 - file_content_selection)*0.01))
index_sec_added_label = np.array(index_sec_added_label)
# print(index_sec_added_label[0]
num = len(index_sec_added_label[0])
Tumor_image_sec = np.zeros(Tumor_image.shape)
for kk in range(0,num):
    Tumor_image_sec = Tumor_image_sec + (result_label_image == index_sec_added_label[0,kk]) ##一次循环加入一个超像素
Tumor_image_sec = Tumor_image_sec * seg_PET1_image
Tumor_image_sec[Tumor_image_sec == 0] = 255
misc.imsave(r'C:\Users\XML\PycharmProjects\DeepLearning\Tkinter\test/TumorPercent-{}.png'.format(xx),Tumor_image_sec)
