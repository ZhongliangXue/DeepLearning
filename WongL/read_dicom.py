#-*-coding:utf-8-*-
import importlib
import sys
#importlib.reload(sys)
import cv2
import numpy
import pydicom
from matplotlib import pyplot as plt
import os
import numpy as np
import SimpleITK as sitk

def load_scan(path):
    slices = [pydicom.read_file(path + '/' + s) for s in os.listdir(path)]
    #slices.sort(key = lambda x: int(x.ImagePositionPatient[2]))
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

def loadFileInformation(filename):
    information = {}
    ds = pydicom.read_file(filename)
    information['PatientID'] = ds.PatientID
    information['PatientName'] = ds.PatientName
    information['PatientBirthDate'] = ds.PatientBirthDate
    information['PatientSex'] = ds.PatientSex
    information['StudyID'] = ds.StudyID
    information['StudyDate'] = ds.StudyDate
    information['StudyTime'] = ds.StudyTime
    information['InstitutionName'] = ds.InstitutionName
    information['Manufacturer'] = ds.Manufacturer
    print(dir(ds))
    print(type(information))
    return information

def read_dicom(filename):
    dcm = pydicom.read_file(filename)
    #print ('aaaa')
    #print (dcm.pixel_array)
    dcm.image = dcm.pixel_array * dcm.RescaleSlope + dcm.RescaleIntercept
    slices = []
    slices.append(dcm)
    img = slices[int(len(slices) / 2)].image.copy()   
    ret, img = cv2.threshold(img, 90, 3071, cv2.THRESH_BINARY)
    img = numpy.uint8(img)
    plt.imshow(img)
    im2, contours = cv2.findContours(img,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    #print contours
    mask = numpy.zeros(img.shape, dtype='uint8')
    for contour in contours:
        cv2.fillPoly(mask, [contour], 255)
    img[(mask > 0)] = 255
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
    img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
    img2 = slices[int(len(slices) / 2)].image.copy()
    img2[(img == 0)] = -2000
    plt.figure(figsize=(12, 12))
    plt.subplot(131)
    plt.imshow(slices[int(len(slices) / 2)].image, 'gray')
    plt.title('Original')
    plt.subplot(132)
    plt.imshow(img, 'gray')
    plt.title('Mask')
    plt.subplot(133)
    plt.imshow(img2, 'gray')
    plt.title('Result')
    plt.show()

def convert_dcm_to_mhd(dcmFilesList, DirName, SavePath):
    # 第一步：将第一张图片作为参考图片，并认为所有图片具有相同维度
    RefDs = pydicom.read_file(dcmFilesList[0])  # 读取第一张dicom图片
    #
    # 第二步：得到dicom图片所组成3D图片的维度
    ConstPixelDims = (int(RefDs.Rows), int(RefDs.Columns), len(dcmFilesList))  # ConstPixelDims是一个元组
    #
    # 第三步：得到x方向和y方向的Spacing并得到z方向的层厚
    ConstPixelSpacing = (float(RefDs.PixelSpacing[0]), float(RefDs.PixelSpacing[1]), float(RefDs.SliceThickness))
    #
    # 第四步：得到图像的原点
    Origin = RefDs.ImagePositionPatient

    # 根据维度创建一个numpy的三维数组，并将元素类型设为：pixel_array.dtype
    ArrayDicom = np.zeros(ConstPixelDims, dtype=RefDs.pixel_array.dtype)  # array is a numpy array
    #
    # 第五步:遍历所有的dicom文件，读取图像数据，存放在numpy数组中。并做像素值到HU值的转换。
    ArrayDicom = load_scan(DirName)
    ArrayDicom = get_pixels_hu(ArrayDicom)

    # 第六步：将现在的numpy数组通过SimpleITK转化为mhd和raw文件
    sitk_img = sitk.GetImageFromArray(ArrayDicom, isVector=False)
    sitk_img.SetSpacing(ConstPixelSpacing)
    sitk_img.SetOrigin(Origin)
    sitk.WriteImage(sitk_img, SavePath)

if __name__ == "__main__":
    #dicom_file = "./DICOM_Seg/test/1.3.6.1.4.1.14519.5.2.1.6279.6001.305189064097515992297956054616.dcm"
    dicom_file1 = r"E:\LeStudy\MyPythonCode\PyCharmProjects\src\Lung\DICOM_Seg\20180113\P97176\SE01\IM000000"
    dicom_file = r"000001.dcm"
    dicom_Input_Folder = './DICOM_Seg/dataset/lung/'# 与python文件同一个目录下的文件夹,存储dicom文件
    ct_mhd_Save_Folder = './DICOM_Seg/dataset/lung_ct_SaveRaw/'
    mask_mhd_Save_Folder = './DICOM_Seg/dataset/lung_mask_SaveRaw/'# 与python文件同一个目录下的文件夹,用来存储肺部mask的mhd文件和zraw文件
    DcmFilesList = []
    PatientPath = 'P90000001'
    read_dicom(dicom_file)
    # lung_dicom_path = dicom_Input_Folder + PatientPath + '/SE01'
    # for dirName, subdirList, fileList in os.walk(lung_dicom_path):
    #     for filename in fileList:
    #         DcmFilesList.append(os.path.join(dirName, filename))
    #     ct_mhd_path = os.path.join(ct_mhd_Save_Folder, PatientPath + 'SE01' + ".mhd")
    #     ArrayDicom = load_scan(dirName)
    #     #convert_dcm_to_mhd(DcmFilesList,dirName, ct_mhd_path)
    #     print(DcmFilesList)
    #     print(ArrayDicom)
    #     DcmFilesList = []#clear!!!


    # a = pydicom.read_file(dicom_file)
    # print(a.pixel_array.shape)
    # print(a.RescaleIntercept)
    # print(a.RescaleSlope)
    # print(a.pixel_array)
    # patient_lung_pixels = a.pixel_array * a.RescaleSlope + a.RescaleIntercept
    # plt.hist(patient_lung_pixels.flatten(),bins=80,color='c')
    # plt.show()
    #plt.savefig(PatientPath+'.png')
    seriesIdSet = set()
    BodyPartExaminedSet = set()
    ModalitySet = set()
    seriesId_Modality_BPE_dict = {}
    if not seriesId_Modality_BPE_dict:
        print('seriesId_Modality_BPE_dict 为空')
    input_path = r'E:\LeStudy\ML\机器学习自学\(6)已自学的工程\DICOM肺部分割\给上海的资料\代码版本\V_DeepLung_W1.6\Nodule_Detection_Code\test'
    for dirName, subdirList, fileList in os.walk(input_path):
        if (len(fileList) == 0):
            ErrorCode = '-1'
            ErrorMessage = "请选择一个CT属性为'CHEST'的非空文件夹!"
            print('Error!')
        else:
            for filename in fileList:
                try:
                    ct_img = pydicom.read_file(os.path.join(dirName, filename))  # 此步过滤了非DICOM文件。
                except:
                    # ErrorCode = '-2'
                    # ErrorMessage = "请确保所选文件夹仅含CT文件!"
                    # make_XML_print(SeriesId, ErrorCode, ErrorMessage, '')
                    # return
                    pass
                try:
                    # if (ct_img.BodyPartExamined == 'CHEST'):
                        seriesIdSet.add(ct_img.SeriesInstanceUID)
                        ModalitySet.add(ct_img.Modality)
                        BodyPartExaminedSet.add(ct_img.BodyPartExamined)
                        seriesId_Modality_BPE_dict[ct_img.SeriesInstanceUID] = [ct_img.Modality,ct_img.BodyPartExamined]
                except:
                    pass
        print(seriesIdSet)
        print(ModalitySet)
        print(BodyPartExaminedSet)
        print(seriesId_Modality_BPE_dict)
        break#不继续往下查找，跳出for循环
    seriesid = ''#'1.3.12.2.1107.5.1.4.1007.30000017010221335598400005860'
    for dict_item_seriesid, dict_item_Modality_and_BPE in seriesId_Modality_BPE_dict.items():
        if seriesid == '':
            if(dict_item_Modality_and_BPE[0]=='CT' and dict_item_Modality_and_BPE[1]=='CHEST'):
                seriesid = dict_item_seriesid
                break
        else:
            if seriesid in seriesId_Modality_BPE_dict:
                if (seriesId_Modality_BPE_dict[seriesid][0] == 'CT' and seriesId_Modality_BPE_dict[seriesid][1] == 'CHEST'):
                    print('OK,its in the dict!')
                    break
    print(seriesid)