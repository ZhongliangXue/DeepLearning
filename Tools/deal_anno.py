#encoding:utf-8
import os
import cv2
import json
import SimpleITK as sitk
import numpy as np
from skimage.filters import roberts
from scipy import ndimage as ndi
import scipy.io as sio
import nibabel as nib

def process_label(filepath):
    # 将真实标注转化为需要的.png格式
    num = 0
    folder_seg = os.path.join(os.path.dirname(filepath),'liver_seg')
    if not os.path.exists(folder_seg): os.makedirs(folder_seg)
    for file in sorted(os.listdir(filepath),reverse=True):
        file_for_slice_seg = os.path.join(folder_seg,'seg-{}.png'.format(num))
        label = read_anno(os.path.join(filepath,file))
        cv2.imwrite(file_for_slice_seg,label*255)
        num += 1

def read_anno(annoname):                      #标注文件anno格式
    with open(annoname) as file:
        x_y_list = file.readline()
        Nodule_Attributions_Dict = json.loads(x_y_list)
        Coords = Nodule_Attributions_Dict['Coords']
        CoordsX = Coords[0::2]
        CoordsY = Coords[1::2]
        anno = np.zeros((1024,1024))

        anno[CoordsX,CoordsY] = 1
        edges = roberts(anno)
        anno = ndi.binary_fill_holes(edges)

    return np.rot90(anno)

# 将上海给定的肝标注数据转化为Nii格式
def save_nii(ct_path, label_path):
    # 读取ct数据，用于求分辨率和原点
    ct = sitk.ReadImage(ct_path, sitk.sitkInt16)
    ct_data = sitk.GetArrayFromImage(ct)
    print('the shape of ct:',ct_data.shape)
    name = os.path.basename(ct_path).split('.')[0].replace('volume','segmentation')
    # 将标注文件处理成矩阵格式
    label = []
    for file in sorted(os.listdir(label_path),reverse=True):
        label_slice = read_anno(os.path.join(label_path,file))
        label_slice = np.array(label_slice)
        label_slice = label_slice.astype(int)
        label.append(label_slice)
    label = np.array(label)
    label = label.astype(int)
    save_path = os.path.join(os.path.dirname(os.path.dirname(ct_path)),'seg')
    if not os.path.exists(save_path): os.makedirs(save_path)
    label = np.array(label)
    print('the shape of label:',label.shape)
    label = sitk.GetImageFromArray(label)
    label.SetDirection(ct.GetDirection())
    label.SetOrigin(ct.GetOrigin())
    label.SetSpacing(ct.GetSpacing())
    print('step 1')
    sitk.WriteImage(label, os.path.join(save_path,name+'.nii'))
    print('step 2')

if __name__ == '__main__':
    # filepath = r'F:\BaiduNetdiskDownload\EightPatients\ZS15127160\SE03'
    # process_label(filepath)

    ct_nii_path = r'C:\Users\XML\Desktop\train_VNet\DiCOM2nii\volume-372.nii'
    seg_anno_path = r'F:\实验室\9LiverAndSeg\P00001372\anno'
    save_nii(ct_nii_path,seg_anno_path)





