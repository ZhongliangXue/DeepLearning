import SimpleITK as sitk
from scipy.ndimage.morphology import binary_dilation,generate_binary_structure
from skimage.morphology import convex_hull_image
from PIL import Image
import cv2
from matplotlib import pyplot as plt
import numpy as np
import os

def load_itk_image(filename):
    with open(filename) as f:
        contents = f.readlines()
        line = [k for k in contents if k.startswith('TransformMatrix')][0]
        transformM = np.array(line.split(' = ')[1].split(' ')).astype('float')
        transformM = np.round(transformM)
        if np.any(transformM != np.array([1, 0, 0, 0, 1, 0, 0, 0, 1])):
            isflip = True
        else:
            isflip = False

    itkimage = sitk.ReadImage(filename)
    numpyImage = sitk.GetArrayFromImage(itkimage)  # indexes are z,y,x (notice the ordering)

    numpyOrigin = np.array(list(reversed(itkimage.GetOrigin())))
    numpySpacing = np.array(list(reversed(itkimage.GetSpacing())))

    return numpyImage, numpyOrigin, numpySpacing, isflip

def VoxelToWorldCoord(voxelCoord, origin, spacing):
    strechedVocelCoord = voxelCoord * spacing
    worldCoord = strechedVocelCoord + origin
    return worldCoord

#file_name = 'E:\\LeStudy\\MyPythonCode\\PyCharmProjects\\src\\Lung\\DICOM_seg\\test\\P90000001SE01.mhd'
file_name = 'E:\\LeStudy\\MyPythonCode\\PyCharmProjects\\src\\Lung\\DICOM_seg\\test\\1.3.6.1.4.1.14519.5.2.1.6279.6001.105756658031515062000744821260.mhd'
#file_name = 'E:\\LeStudy\\MyPythonCode\\PyCharmProjects\\src\\Lung\\LUNA16\\1.3.6.1.4.1.14519.5.2.1.6279.6001.100225287222365663678666836860mask\\1.3.6.1.4.1.14519.5.2.1.6279.6001.100225287222365663678666836860.mhd'
#file_name = 'E:\\LeStudy\\MyPythonCode\\PyCharmProjects\\src\\Lung\\DICOM_seg\\dataset\\lung_mask_SaveRaw\\P90000008SE01_mask.mhd'
# path =  file_name[:-4] + '\\'
# if not os.path.exists(path):
#     os.mkdir(path)
img = sitk.ReadImage(file_name)
img_array = sitk.GetArrayFromImage(img)
print(img)

# for i, im in enumerate(img_array):
#   cv2.imwrite(os.path.join(path, '{}.png'.format(i)), im*255)
