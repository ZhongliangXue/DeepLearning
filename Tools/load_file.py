import nrrd
import time
import os
import SimpleITK as sitk
import dicom2nifti
import nibabel as nib

def test_loadnrrd(nrrd_path):
    start_time = time.clock()
    nrrd_data, nrrd_options = nrrd.read(nrrd_path)
    end_time = time.clock()
    print(nrrd_data)
    print('加载nrrd数据消耗时间：' + str((end_time - start_time)) + '秒。')
    print(nrrd_options)

def test_loadDICOM(DICOM_path):
    lstFilesDCM = []
    start_time = time.clock()
    ##将一个文件夹下的所有的DICOM文件的路径保存到一个列表中
    for dirName, subdirList, fileList in os.walk(DICOM_path):
        for filename in fileList:
            if ".dcm" in filename.lower():  ##判断是否为dicom文件
                print(filename)
                lstFilesDCM.append(os.path.join(dirName, filename))
    ##遍历所有的DICOM文件
    for i in range(0, len(lstFilesDCM)):
        data = sitk.ReadImage(lstFilesDCM[i])
        image_array = sitk.GetArrayFromImage(data)
        print(image_array)
    end_time = time.clock()
    print('DICOM的文件加载时间：' + str((end_time - start_time)) + '秒。')

def test_loadNifty(Nifty_path):
    start_time = time.clock()
    data = nib.load(Nifty_path)
    array = data.get_data()
    print(array)
    end_time = time.clock()
    print('Nifty文件的加载时间为：'+ str((end_time - start_time)) + '秒。')

def dicom2nii(dicom_directory,output_folder):
    dicom2nifti.convert_directory(dicom_directory,output_folder)

if __name__ == '__main__':
    nrrd_path = 'D:\Beijing-302\A00057236/3WB_Std.nrrd'
    test_loadnrrd(nrrd_path)                                                ##35.6095166秒

    # DICOMpath = 'D:\Beijing-302\A00057236\WB_Std_3'
    # test_loadDICOM(DICOMpath)                                             ##5.0577655秒

    # dicom_directory = r'D:\Beijing-302\A00057236\WB_Std_3/'
    # output_folder = r'D:\Beijing-302\A00057236/'
    # dicom2nii(dicom_directory,output_folder)

    # Nifty_path = 'D:\Beijing-302\A00057236/3_wb_std.nii'
    # test_loadNifty(Nifty_path)                                             ##0.0019555秒