import os
import nibabel as nib
import cv2
import numpy as np
import matplotlib.image as mpimg
import SimpleITK as sitk

open_path = r'F:\LabRoom\9LiverAndSeg\ZS15127160/volume-160.nii'
save_file = r'F:\LabRoom\9LiverAndSeg\ZS15127160/'

data = sitk.ReadImage(open_path)
image_array = sitk.GetArrayFromImage(data)

for i in range(10,21):
    save_path = os.path.join(save_file, 'P3-{}.png'.format(i))
    image_array_single = image_array[i,:,:]

    image_array_single[ image_array_single < -200] = -200
    image_array_single[image_array_single > 200] = 200

    print(np.max(image_array_single), np.min(image_array_single))

    ##根据软件的经验，将超过SUV最大值1/4的值截断
    # image_array_single[image_array_single > max_HU] = max_HU
    # image_array_single[image_array_single < min_HU] = min_HU
    # image_array_single = np.rot90(image_array_single,1)
    # image_array_single = cv2.resize(image_array_single, (512, 512), interpolation=cv2.INTER_CUBIC)
    mpimg.imsave(save_path, image_array_single, cmap='gray')


