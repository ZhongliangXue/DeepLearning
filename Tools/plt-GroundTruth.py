#encoding:utf-8
# 作者    ：XML
# 创建时间：2019/6/28 23:17
# 文件    : plt-GroundTruth.py
# IDE     : PyCharm

import SimpleITK as sitk
import matplotlib.pyplot as plt

path = r'D:\SH-Data\20190617\P00057227/P00057227-result.nii'
data = sitk.ReadImage(path)
array = sitk.GetArrayFromImage(data)

single_array = array[18,:,:]
plt.imshow(single_array)
plt.show()