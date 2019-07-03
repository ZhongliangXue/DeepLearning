#encoding:utf-8
# 作者    ：XML
# 创建时间：2019/6/28 15:03
# 文件    : DCMLabel2LiverAndTumor.py
# IDE     : PyCharm

"""
@brief : 这是一个同时处理肝轮廓和肝病灶标注文件的脚本：将标注的肝轮廓和肝病灶DCM文件，处理成.nii文件。
输出的结果为3个文件：肝轮廓（label : 1）、肝病灶(label : 2)、肝轮廓和肝病灶(label : 1 和 2)。

算法流程：
1. 两个标注DCM的文件夹读进来，路径存储到两个list中.
2. 分别处理两个文件夹中的文件，处理成与原始CT相同大小的数据。且分别存储在两个 三维 矩阵中.
3. 因为肝病灶的数量是不连续且较少的：根据肝病灶DCM的文件名和肝轮廓DCM的文件名，找到肝轮廓对应的index.得到一个0、1、2标记的矩阵
4. 由原始CT中的头文件信息，将三个矩阵分别存为.nii格式的数据.
"""

from skimage.filters import roberts
from scipy import ndimage as ndi
import os
import pydicom
import numpy as np
import SimpleITK as sitk
import cv2

# 将原来的矩形图像，裁剪成正方形，且放缩到原始ct的大小
def anno_process_cut(anno_data, ct_size):
    '''
    :param anno_data: 初步处理后的anno标注数据，非规则的二维矩阵
    :return: 裁剪后的，默认为512*512大小的矩阵：如果原始切片为1024*1024，可以使用其他工具放缩。
    '''
    imageHight = anno_data.shape[0]
    imageWidth = anno_data.shape[1]
    anno_data = anno_data[:,int((imageWidth - imageHight)/2):int(imageWidth - (imageWidth - imageHight)/2)]
    anno_data = ndi.zoom(anno_data, (ct_size/imageHight, ct_size/imageHight), order=3)

    return anno_data

# 将一个3D的array，结合原始ct序列中的头文件信息，存储为一个.nii文件。
def save_array3D_And_CT_to_nii(ctDir_path, array3D, niiSaveDir, niiName):
    ctOriginDCM = []
    for root, subdirList, fileList in os.walk(ctDir_path):
        for ctFile in fileList:
            ctOriginDCM.append(os.path.join(root, ctFile))

    ctSlices = [pydicom.read_file(k) for k in ctOriginDCM]
    ctSlices.sort(key = lambda x : int(x.ImagePositionPatient[2]), reverse=False)

    try:
        slice_thickness = np.abs(ctSlices[0].ImagePositionPatient[2] - ctSlices[1].ImagePositionPatient[2])
    except:
        slice_thickness = np.abs(ctSlices[0].SliceLocation - ctSlices[1].SliceLocation)

    ConstPixelSpacing = (float(ctSlices[0].PixelSpacing[0]),
                         float(ctSlices[0].PixelSpacing[1]),
                         float(slice_thickness))
    Origin = ctSlices[0].ImagePositionPatient
    array3D = np.array(array3D)

    sitk_img = sitk.GetImageFromArray(array3D)
    sitk_img.SetOrigin(Origin)
    sitk_img.SetSpacing(ConstPixelSpacing)
    sitk.WriteImage(sitk_img, os.path.join(niiSaveDir, niiName))

    return

# 处理肝标注和肝病灶标注的DCM文件夹,将处理得到的数据进行融合，存储在一份.nii文件中。
def process_LiverAndTumor_DCM(liverDCM_Dir, tumorDCM_Dir, ctDir, savePath, fileName):

    # 读取原始ct文件夹 =》 得到图像的size
    ctOriginDCM = []
    for root, subdirList, fileList in os.walk(ctDir):
        for ctFile in fileList:
            ctOriginDCM.append(os.path.join(root, ctFile))
    slice = pydicom.read_file(ctOriginDCM[0])
    ct_size = slice.pixel_array.shape[0]

    # 读取肝轮廓标注的DCM文件夹
    liverDCM_List = []        # 存储每个DCM文件的路径
    liverFileList = []        # 存储每个DCM文件的名称，作为index
    for liver_root, liver_subdirlist, liver_fileList in os.walk(liverDCM_Dir):
        for liver_filename in liver_fileList:
            liverDCM_List.append(os.path.join(liver_root, liver_filename))
            liverFileList.append(liver_filename)
    liverSlices = [pydicom.read_file(m) for m in liverDCM_List]

    # 读取肝病灶标注的DCM文件夹
    tumorDCM_List = []
    tumorFileList = []
    for tumor_root, tumor_subdirList, tumor_fileList in os.walk(tumorDCM_Dir):
        for tumorFile in tumor_fileList:
            tumorDCM_List.append(os.path.join(tumor_root, tumorFile))
            tumorFileList.append(tumorFile)
    tumorSlices = [pydicom.read_file(n) for n in tumorDCM_List]

    # 处理肝轮廓标注
    liverArrayList = []
    for liver in range(0, len(liverSlices)):
        single_array = liverSlices[liver].pixel_array
        array_0 = single_array[:,:,0]
        array_1 = single_array[:,:,1]

        index_x, index_y = np.where(array_0 != 0)
        for i in range(index_y.shape[0]):
            array_1[index_x[i], index_y[i]] = 0

        array_1 = np.array(array_1, np.uint8)
        image, contours, hierarchy = cv2.findContours(array_1, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        new_contours = []
        new_hierarchy = []
        for i in range(0, len(contours)):
            area = cv2.contourArea(contours[i])
            if area > 300:
                new_contours.append(contours[i])
                new_hierarchy.append(hierarchy[0, i, :])

        result_liver = np.zeros_like(array_1)
        for j in range(0, len(new_contours)):
            result_liver[new_contours[j][..., 1], [new_contours[j][..., 0]]] = 1

        edges = roberts(result_liver)
        result_liver = ndi.binary_fill_holes(edges).astype(np.uint8)

## —————————————————————————————————————————————————————————————————————
        # ## 填充完了，再检查空洞，把空洞去掉(只对部分切片)
        # if liver == 35:
        #      hole_array = np.zeros_like(array_1)
        #      for i in range(0, len(new_hierarchy)):
        #          if (new_hierarchy[i][2] >= 0 and new_hierarchy[i][2] <= len(new_hierarchy) ):# and cv2.contourArea(new_contours[i]) < 2000
        #              id = new_hierarchy[i][2]
        #              hole_array[new_contours[id][..., 1], [new_contours[id][..., 0]]] = 2
        #
        #      hole_edges = roberts(hole_array)
        #      hole_array = ndi.binary_fill_holes(hole_edges).astype(np.uint8)
        #
        #      x, y = np.where(hole_array != 0)
        #      for v in range(0, x.shape[0]):
        #          result_liver[x[v], y[v]] = 0

        # # 通过膨胀腐蚀操作，去除连通域相接壤的问题（只对部分切片）
        if liver == 80 :
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
            result_liver = cv2.dilate(result_liver, kernel, iterations=2)
            result_liver = cv2.erode(result_liver, kernel, iterations=1)

## —————————————————————————————————————————————————————————————————————

        result_liver = anno_process_cut(anno_data = result_liver, ct_size = ct_size)
        liverArrayList.append(result_liver)

    liverArray3D = np.array(liverArrayList)

    # 处理肝病灶标注
    tumorArrayList = []
    for tumor in range(0, len(tumorSlices)):
        single_array = tumorSlices[tumor].pixel_array
        array_0 = single_array[:,:,0]
        array_1 = single_array[:,:,1]

        index_x, index_y = np.where(array_0 != 0)
        for i in range(index_x.shape[0]):
            array_1[index_x[i], index_y[i]] = 0

        array_1 = np.array(array_1, np.uint8)
        image, contours, hierarchy = cv2.findContours(array_1, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        new_contours = []
        new_hierarchy = []
        for i in range(0, len(contours)):
            area = cv2.contourArea(contours[i])
            if area > 220:
                new_contours.append(contours[i])
                new_hierarchy.append(hierarchy[0, i, :])

        result_tumor = np.zeros_like(array_1)
        for j in range(0, len(new_contours)):
            result_tumor[new_contours[j][..., 1], [new_contours[j][..., 0]]] = 2

        edges = roberts(result_tumor)
        result_tumor = ndi.binary_fill_holes(edges).astype(np.uint8)
        result_tumor = anno_process_cut(anno_data = result_tumor, ct_size = ct_size)
        tumorArrayList.append(result_tumor)

    tumorArray3D = np.array(tumorArrayList)

    ## 根据肝轮廓标注和肝病灶标注的数据，融合生成一份3DArray数据

    # 使用列表assertIndex，来存储病灶切片对应在CT序列中的位置
    firstSliceIndex = liverFileList[0]
    firstSliceIndex = np.uint8(firstSliceIndex)
    assertIndex = []
    for i in range(0, len(tumorFileList)):
        index = tumorFileList[i]
        index = np.uint8(index)
        assertIndex.append(np.uint8(index - firstSliceIndex))

    resultArray3D = liverArray3D
    for j in range(0, tumorArray3D.shape[0]):
        index_x ,index_y = np.where(tumorArray3D[j,:,:] != 0)
        for k in range(index_y.shape[0]):
            resultArray3D[assertIndex[j], index_x[k], index_y[k]] = 2

    save_array3D_And_CT_to_nii(ctDir_path = ctDir, array3D = resultArray3D, niiSaveDir = savePath, niiName = fileName)

    return

if __name__ == "__main__":
    liverDCM_Dir = r'D:\SH-Data\20190617\P00057228\肝部轮廓'
    tumorDCM_Dir = r'D:\SH-Data\20190617\P00057228\肝部病灶'
    ctDir = r'D:\SH-Data\20190617\P00057228\CT'
    savePath = r'D:\SH-Data\20190617\P00057228'
    fileName = r'P00057228-result.nii'

    process_LiverAndTumor_DCM(liverDCM_Dir, tumorDCM_Dir, ctDir, savePath, fileName)
