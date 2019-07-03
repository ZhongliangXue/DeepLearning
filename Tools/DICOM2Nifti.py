import dicom2nifti

##转换一个文件夹中的全部DICOM序列为一个nii文件
def dicomseries2nifti(input_path,save_path):
    dicom2nifti.convert_directory(input_path, save_path, compression=True, reorient=True)

def dicomfile2nifti(input_path,save_path):
    dicom2nifti.dicom_series_to_nifti(input_path,save_path,reorient_nifti=True)

if __name__ == "__main__":
####———————————————— Test 1————————————————————————
    input_path = r'F:\LabRoom\9LiverAndSeg\ZS15127160\SE01'
    save_path = r'F:\LabRoom\9LiverAndSeg\ZS15127160\SE01/'
    dicomseries2nifti(input_path,save_path)