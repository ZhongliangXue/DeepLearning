# -*- coding:utf-8 -*-
'''
This script is used for Format Transformation and Generate Mask of Lung
Packages: SimpleITK, pydicom, skimage, scipy, numpy, csv.
'''
import argparse
import glob
import os
import SimpleITK as sitk
import numpy as np
import skimage
from skimage.morphology import ball, disk, dilation, binary_erosion, remove_small_objects, erosion, closing, reconstruction, binary_closing
from skimage.measure import label,regionprops, perimeter
from skimage.morphology import binary_dilation, binary_opening
from skimage.filters import roberts, sobel
from skimage import measure, feature
from skimage.segmentation import clear_border
from skimage import data
from scipy import ndimage as ndi
import scipy.misc
import csv
#import cv2
import pydicom
parser = argparse.ArgumentParser(description='MedasLungPreprocess')
parser.add_argument('--dicom_folder', '-df', metavar='Dicom Parent Directory',
                    help='Please input CHEST Dicom Folder include all train datas!')

# Load the scans in given folder path
def load_scan(dcmFilesPathList):
    slices = [pydicom.read_file(i) for i in dcmFilesPathList]#(path + '/' + s) for s in os.listdir(path)]
    slices.sort(key = lambda x: int(x.ImagePositionPatient[2]), reverse = False)
    try:
        slice_thickness = np.abs(slices[0].ImagePositionPatient[2] - slices[1].ImagePositionPatient[2])
    except:
        slice_thickness = np.abs(slices[0].SliceLocation - slices[1].SliceLocation)
    for s in slices:
        s.SliceThickness = slice_thickness
    return slices

def get_pixels_hu(slices):
    image = np.stack([s.pixel_array for s in slices])
    # Convert to int16 (from sometimes int16),
    # should be possible as values should always be low enough (<32k)
    image = image.astype(np.int16)
    # Set outside-of-scan pixels to 0
    # The intercept is usually -1024, so air is approximately 0
    image[image == -2000] = 0
    # Convert to Hounsfield units (HU),当处理特殊CT时以下临时注释。
    for slice_number in range(len(slices)):
        intercept = slices[slice_number].RescaleIntercept
        slope = slices[slice_number].RescaleSlope
        if slope != 1:
            image[slice_number] = slope * image[slice_number].astype(np.float64)
            image[slice_number] = image[slice_number].astype(np.int16)
        image[slice_number] += np.int16(intercept)
    return np.array(image, dtype=np.int16)

def mkdir_from_style(dicom_Input_Folder,mhd_Save_Folder):
#生成与原始图像相同目录层级的目录。
    if not os.path.exists(mhd_Save_Folder):
        os.mkdir(mhd_Save_Folder)
    for PatientPath in os.listdir(dicom_Input_Folder):
        if not os.path.exists(mhd_Save_Folder + '/' + PatientPath):
            os.mkdir(mhd_Save_Folder + '/' + PatientPath)
            for SerisePath in os.listdir(dicom_Input_Folder + PatientPath):
                os.mkdir(mhd_Save_Folder + PatientPath + '/' + SerisePath)

def convert_dcm_to_mhd(dcmFilesList, SavePath):
    # 第一步：将第一张图片作为参考图片，并认为所有图片具有相同维度
    RefDs = pydicom.read_file(dcmFilesList[0])  # 读取第一张dicom图片
    #print(dcmFilesList)
    # 第二步：得到dicom图片所组成3D图片的维度
    ConstPixelDims = (int(RefDs.Rows), int(RefDs.Columns), len(dcmFilesList))  # ConstPixelDims是一个元组
    # 第三步：得到x方向和y方向的Spacing并得到z方向的层厚
    ConstPixelSpacing = (float(RefDs.PixelSpacing[0]), float(RefDs.PixelSpacing[1]), float(RefDs.SliceThickness))
    # 第四步：得到图像的原点
    Origin = RefDs.ImagePositionPatient
    # 根据维度创建一个numpy的三维数组，并将元素类型设为：pixel_array.dtype
    ArrayDicom = np.zeros(ConstPixelDims, dtype=RefDs.pixel_array.dtype)  # array is a numpy array
    # 第五步:遍历所有的dicom文件，读取图像数据，存放在numpy数组中。并做像素值到HU值的转换。
    ArrayDicom = load_scan(dcmFilesList)
    ArrayDicom = get_pixels_hu(ArrayDicom)
    # 第六步：将现在的numpy数组通过SimpleITK转化为mhd和raw文件
    sitk_img = sitk.GetImageFromArray(ArrayDicom, isVector=False)
    sitk_img.SetSpacing(ConstPixelSpacing)
    sitk_img.SetOrigin(Origin)
    sitk.WriteImage(sitk_img, SavePath)

def generate_3d_mask(DcmFilesList, image, save_path):
    # Position the scan upright,
    # so the head of the patient would be at the top facing the camera
    lstFilesDCM = DcmFilesList
    RefDs = pydicom.read_file(lstFilesDCM[0])
    ConstPixelDims = (int(RefDs.Rows), int(RefDs.Columns), len(lstFilesDCM))
    ConstPixelSpacing = (float(RefDs.PixelSpacing[0]), float(RefDs.PixelSpacing[1]), float(RefDs.SliceThickness))
    Origin = RefDs.ImagePositionPatient
    sitk_img = sitk.GetImageFromArray(image, isVector=False)
    sitk_img.SetSpacing(ConstPixelSpacing)
    sitk_img.SetOrigin(Origin)
    sitk.WriteImage(sitk_img, save_path, True)#True -> zraw, Default -> raw

def generate_2D_slices(file_path, flag = 'ct'):
    #Read mask mhd/zraw file and generate mask 2D slices
    ct_2D_store_path = file_path[:-4] + '/'
    if not os.path.exists(ct_2D_store_path):
        os.mkdir(ct_2D_store_path)
    img = sitk.ReadImage(file_path)
    img_array = sitk.GetArrayFromImage(img)
    if flag == 'mask':
        for i, im in enumerate(img_array):
            cv2.imwrite(os.path.join(ct_2D_store_path, '{}.png'.format(i+1)), im*255)
    elif flag == 'ct':
        windowwidth = 1200 # 窗宽
        windowcenter = -600  # 窗位
        CT_max = (2 * windowcenter + windowwidth) / 2
        CT_min = (2 * windowcenter - windowwidth) / 2
        disp_pixel = (img_array - CT_min) * 255.0 / float(CT_max - CT_min)
        disp_pixel[disp_pixel > 255] = 255
        disp_pixel[disp_pixel < 0] = 0
        for i, im in enumerate(disp_pixel):
            cv2.imwrite(os.path.join(ct_2D_store_path, '{}.png'.format(i+1)), im)
    else:
        print('Please indicate mask or ct!')

def get_segmented_lungs(im, plot=False):
    '''
    This funtion segments the lungs from the given 2D slice.
    '''
    if plot == True:
        f, plots = plt.subplots(8, 1, figsize=(5, 40))
    '''
    Step 1: Convert into a binary image.
    '''
    binary = im < -320#604#算法改进，先2D处理再3D处理。
    if plot == True:
        plots[0].axis('off')
        plots[0].set_title('binary image')
        plots[0].imshow(binary, cmap=plt.cm.bone)
    '''
    Step 2: Remove the blobs connected to the border of the image.
    '''
    cleared = clear_border(binary)
    if plot == True:
        plots[1].axis('off')
        plots[1].set_title('after clear border')
        plots[1].imshow(cleared, cmap=plt.cm.bone)
    '''
    Step 3: Label the image.
    '''
    label_image = label(cleared)
    if plot == True:
        plots[2].axis('off')
        plots[2].set_title('found all connective graph')
        plots[2].imshow(label_image, cmap=plt.cm.bone)
    '''
    Step 4: Keep the labels with 2 largest areas.
    '''
    areas = [r.area for r in regionprops(label_image)]
    areas.sort()
    if len(areas) > 2:
        for region in regionprops(label_image):
            if region.area < areas[-2]:
                for coordinates in region.coords:
                       label_image[coordinates[0], coordinates[1]] = 0
    binary = label_image > 0
    if plot == True:
        plots[3].axis('off')
        plots[3].set_title(' Keep the labels with 2 largest areas')
        plots[3].imshow(binary, cmap=plt.cm.bone)
    '''
    Step 5: Erosion operation with a disk of radius 2. This operation is
    seperate the lung nodules attached to the blood vessels.
    '''
    selem = disk(2)
    binary = binary_erosion(binary, selem)
    if plot == True:
        plots[4].axis('off')
        plots[4].set_title('seperate the lung nodules attached to the blood vessels')
        plots[4].imshow(binary, cmap=plt.cm.bone)
    '''
    Step 6: Closure operation with a disk of radius 10. This operation is
    to keep nodules attached to the lung wall.
    '''
    selem = disk(10)
    binary = binary_closing(binary, selem)
    if plot == True:
        plots[5].axis('off')
        plots[5].set_title('keep nodules attached to the lung wall')
        plots[5].imshow(binary, cmap=plt.cm.bone)
    '''
    Step 7: Fill in the small holes inside the binary mask of lungs.
    '''
    edges = roberts(binary)
    binary = ndi.binary_fill_holes(edges)
    if plot == True:
        plots[6].axis('off')
        plots[6].set_title('Fill in the small holes inside the binary mask of lungs')
        plots[6].imshow(binary, cmap=plt.cm.bone)
    # '''
    # Step 8: Superimpose the binary mask on the input image.
    # '''
    # get_high_vals = binary == 0
    # im[get_high_vals] = 0
    # if plot == True:
    #     plots[7].axis('off')
    #     plots[7].set_title('Superimpose the binary mask on the input image')
    #     plots[7].imshow(im, cmap=plt.cm.bone)
    return binary

def segment_lung_mask(image):
    binary_image = image
    labels = measure.label(binary_image, background=0)
    vals, counts = np.unique(labels, return_counts=True)
    counts = counts[vals != 0]
    vals = vals[vals != 0]
    counts_and_vals = sorted(zip(counts, vals), key=lambda x: -x[0])
    if len(counts) == 0:
        print('Error: len(counts)=0')
    max_label_counts, max_label = counts_and_vals[0]
    if len(counts) == 1:
        binary_image[labels != max_label] = 0
    max2_label_counts, max2_label = counts_and_vals[1]
    if max2_label_counts > 0.2 * max_label_counts:
        binary_image[(labels != max_label) & (labels != max2_label)] = 0
    else:
        binary_image[labels != max_label] = 0
    return binary_image

def readCSV(filename):
    lines = []
    with open(filename, "rt") as f:
        csvreader = csv.reader(f)
        for i,line in enumerate(csvreader):
            if i != 0:
                lines.append(line)
    return lines

def writeSuidsCSV(filename,mhd_Save_Folder):
    ##生成seriesuids.csv用于FROC评估。
    suid_List = []
    firstline = ['seriesuid']
    for suid in os.listdir(mhd_Save_Folder):
        if suid.endswith('.mhd'):
            suid_List.append(suid[:-4])
    with open(filename, 'wt', newline='') as f:#若不指定newline=''则会每写一行后写一个空行。
        fwriter = csv.writer(f)
        fwriter.writerow(firstline)
        for row in suid_List:
            fwriter.writerow([row])

def DcmtoMhd_and_GenerateMask():
    global args
    args = parser.parse_args()
    dicom_Input_Folder = args.dicom_folder  # DICOM_PATH:Train->Patient->SE01
    # dicom_Input_Folder = r'E:\LeStudy\MyPythonCode\PyCharmProjects\src\Lung\DICOM_Seg\lung_20180417'#Test for myself!
    ### 新建存放CT和mask文件的路径。
    ct_mhd_Save_Folder = dicom_Input_Folder + '/../' + './lung_CT_Train/'  # 用来存储肺部CT的mhd文件和raw文件
    mask_mhd_Save_Folder = dicom_Input_Folder + '/../' + './lung_Mask_Train/'  # 用来存储肺部mask的mhd文件和zraw文件
    DcmFilesList = []
    ### 新建路径
    if not os.path.exists(ct_mhd_Save_Folder):
        os.mkdir(ct_mhd_Save_Folder)
    if not os.path.exists(mask_mhd_Save_Folder):
        os.mkdir(mask_mhd_Save_Folder)
    ### 循环处理
    for PatientPath in os.listdir(dicom_Input_Folder):
        if os.path.isdir(dicom_Input_Folder + '/' + PatientPath):
            print('Process PatientPath:', PatientPath)
            lung_dicom_path = dicom_Input_Folder + '/' + PatientPath + '/SE01'
            if os.path.exists(lung_dicom_path):  # 可能不存在SE01
                for dirName, subdirList, fileList in os.walk(lung_dicom_path):
                    if (len(fileList) == 0):  # 文件夹可能为空，跳出
                        return
                    else:
                        for filename in fileList:
                            try:
                                ct_img = pydicom.read_file(os.path.join(dirName, filename))#此步过滤了非DICOM文件和不含所查tag的DICOM。
                                if (ct_img.Modality == 'CT') and (ct_img.BodyPartExamined == 'CHEST'):
                                    DcmFilesList.append(os.path.join(dirName, filename))
                            except:
                                pass
                        if DcmFilesList:  # 排除人工挑选时SE01可能成了PET等类型的差错
                            DcmFilesList.sort(key=lambda x: int((pydicom.read_file(x)).ImagePositionPatient[2]),
                                              reverse=False)#以最后一张CT为原点
                            ds = pydicom.read_file(os.path.join(dirName, fileList[0]))
                            suid = ds.SeriesInstanceUID
                            ct_mhd_path = os.path.join(ct_mhd_Save_Folder, str(suid) + ".mhd")
                            convert_dcm_to_mhd(DcmFilesList, ct_mhd_path)
                            #generate_2D_slices(ct_mhd_path, flag='ct')#可视化查看是否正常转化格式
                            lung_mask_mhd_path = os.path.join(mask_mhd_Save_Folder, str(suid) + ".mhd")
                            patient_lung = load_scan(DcmFilesList)
                            patient_lung_pixels = get_pixels_hu(patient_lung)
                            segmented_lungs = np.stack(
                                [get_segmented_lungs(patient, False) for patient in patient_lung_pixels])
                            segmented_lungs = np.array(segment_lung_mask(segmented_lungs), dtype=np.int8)  # 仅用阈值计算
                            generate_3d_mask(DcmFilesList, segmented_lungs, lung_mask_mhd_path)
                            #generate_2D_slices(lung_mask_mhd_path, flag='mask')#可视化查看是否正常生成mask
                            DcmFilesList = []  # clear!!!
                    break  # 可能还有子文件夹，不继续往下查找，跳出for循环
    print('CT格式转化和mask生成步骤完成!')
    csvFileName = dicom_Input_Folder + '/../' + 'SH_seriesuids.csv'
    writeSuidsCSV(csvFileName, mask_mhd_Save_Folder)  # 写出SUIDs的CSV文件备用

#主程序。从这里进入。
if __name__ == "__main__":
    DcmtoMhd_and_GenerateMask()#命令行传参：DICOM_PATH（Train->Patient->SE01）中的Train目录。