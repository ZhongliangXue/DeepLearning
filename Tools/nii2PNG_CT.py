import os
import nibabel as nib
import cv2
import numpy as np
import matplotlib.image as mpimg

open_path = r'D:\P3/P3.nii'
save_file = r'D:\P3_image/'
data = nib.load(open_path)
image_array = data.get_data()
image_array = np.array(image_array,float)
max_HU = 255
min_HU = -255
for i in range(145,179):
    save_path = os.path.join(save_file, 'P3-{}.png'.format(i))
    image_array_single = image_array[:,:,i]
    ##根据软件的经验，将超过SUV最大值1/4的值截断
    image_array_single[image_array_single > max_HU] = max_HU
    image_array_single[image_array_single < min_HU] = min_HU
    image_array_single = np.rot90(image_array_single,1)
    # image_array_single = cv2.resize(image_array_single, (512, 512), interpolation=cv2.INTER_CUBIC)
    mpimg.imsave(save_path, image_array_single, cmap='gray_r')
    i += 1
