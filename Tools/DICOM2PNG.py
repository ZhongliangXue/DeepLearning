import  SimpleITK as sitk
import matplotlib
import os
import matplotlib.image as mpimg
from scipy import misc
import numpy as np
import cv2

# dicom_path = r'D:\3liver_PET\P3/'
# save_file = r'D:\3liver_PET\P3_image/'
# i = 1
# ##————————读取dicom_path路径下的所有dicom文件，将每张dicom图片保存到save_path文件夹下————————
# for dicom_file in os.listdir(dicom_path):
#     save_path = os.path.join(save_file,'P3-{}.png'.format(i))
#     SingleDicomPath = os.path.join(dicom_path,dicom_file)
#     image = sitk.ReadImage(SingleDicomPath)
#     image_array = sitk.GetArrayFromImage(image)
#     image_array = image_array[0,:,:]
#     ##根据软件的经验，将超过SUV最大值1/4的值截断
#     max = np.max(image_array)
#     image_array[image_array > (0.25*max)] = (0.25*max)
#     image_array = cv2.resize(image_array, (512, 512), interpolation=cv2.INTER_CUBIC)
#     mpimg.imsave(save_path, image_array, cmap='gray_r')
#     i += 1

###———————————————Test——————————————————————————
image = sitk.ReadImage(r'D:\3liver_PET\P1/00000114.dcm')
image_array = sitk.GetArrayFromImage(image)
image_array = image_array[0,:,:]

max = np.max(image_array)
# image_array[image_array > (0.25*max)] = (0.25*max)
# image_array = cv2.resize(image_array, (512, 512), interpolation=cv2.INTER_CUBIC)
# mpimg.imsave('114_original_cut.png', image_array, cmap='gray_r')
cv2.imwrite('0000.png',image_array)

