import SimpleITK as sitk
import nrrd
import numpy as np
import os

# def nrrd2dcm(nrrd_name,dcm_folder):
#     a,inf=nrrd.read(nrrd_name)
#     writer = sitk.ImageFileWriter()
#     dcm=sitk.GetImageFromArray(a)
#     print(inf)
#     dcm.SetSpacing(np.diag(inf['space directions']).tolist())
#     for i in range(a.shape[-1]):
#         writer.SetFileName(os.path.join(dcm_folder,str(i)+'.dcm'))
#         writer.Execute(dcm[:,:,i])
#     print('ok')
# if __name__ == '__main__':
#     nrrd_name=r'D:\Beijing-302\A00057236/Segmentation.seg.nrrd'
#     dcm_folder=r'D:\dicom'
#     nrrd2dcm(nrrd_name,dcm_folder)

