# -*- coding:utf-8 -*-
'''
This script is used for Showing the CT with nodules.
Packages: SimpleITK, pydicom, numpy, csv.
'''
import argparse
import glob
import os
import traceback	
import SimpleITK as sitk
import numpy as np
import csv
import cv2
from PIL import Image, ImageDraw, ImageFont
import pydicom

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

def readCSV(filename):
    lines = []
    with open(filename, "rt") as f:
        csvreader = csv.reader(f)
        for i,line in enumerate(csvreader):
            if i != 0:
                lines.append(line)
    return lines

def LUNA16_nodule_play(nodule_play_2D_path, lung_ct_SaveRaw, csv_file_path, gt_pred_flag=False):#False为pred rusults.
    if not os.path.exists(nodule_play_2D_path):
        os.mkdir(nodule_play_2D_path)
    csv_file = readCSV(csv_file_path)
    for csv_item in csv_file:
        try:
            img = sitk.ReadImage(lung_ct_SaveRaw + csv_item[0] + '.mhd')
            img_array = sitk.GetArrayFromImage(img)
            WW = 1200  # 窗宽
            WL = -600  # 窗位
            CT_max = (2 * WL + WW) / 2
            CT_min = (2 * WL - WW) / 2
            disp_pixel_val = (img_array - CT_min) * 255.0 / float(CT_max - CT_min)
            disp_pixel_val[disp_pixel_val > 255] = 255
            disp_pixel_val[disp_pixel_val < 0] = 0
            shape = img_array.shape
            origin = np.array(img.GetOrigin())
            spacing = np.array(img.GetSpacing())
            z_list = []
            csv_item_2 = []
            for index, item in enumerate(csv_item[1:4]):
                csv_item_2.append(float(item))
            x, y, z = ((csv_item_2 - origin) / spacing)
            x = int(round(x))
            y = int(round(y))
            z = int(round(z))#(origin[2]-float(csv_item[3]))/spacing[2]))
            if z == shape[0]:
                z = shape[0] - 1
            diameter = int((float(csv_item[5])) / spacing[0]/2)  # 结节直径坐标系转换，画图时用半径
            nodule_play_2D_path_paitient = nodule_play_2D_path + csv_item[0]
            if not os.path.exists(nodule_play_2D_path_paitient):
                os.mkdir(nodule_play_2D_path_paitient)
            if gt_pred_flag:
                cv2.imwrite(os.path.join(nodule_play_2D_path, csv_item[0], 'gt_{}.png'.format(shape[0]-z)), disp_pixel_val[z])
                # Image._show(Image.fromarray(disp_pixel_val[z]))
                img_2 = cv2.imread(os.path.join(nodule_play_2D_path, csv_item[0], 'gt_{}.png'.format(shape[0]-z)))
                img_2 = cv2.circle(img_2, (int(x), int(y)), diameter, (0, 0, 255))
                img_3_draw = Image.fromarray(img_2)
                draw = ImageDraw.Draw(img_3_draw)
                font = ImageFont.truetype('./simheittf.ttf', 30, encoding='utf-8')#记得复制ttf
                draw.text((0, 0), 'Pixel Coord (' + str(float('%.2f' % x)) + ', ' + str(float('%.2f' % y)) + ')', (0, 0, 255), font=font)
                draw.text((0, 35), 'Pred Prob ' + str(float('%.2f' % (float(csv_item[4]) * 100))) + '%', (0, 0, 255), font=font)
                img_4 = np.array(img_3_draw)
                cv2.imwrite(os.path.join(nodule_play_2D_path, csv_item[0], 'gt{}-N'.format(shape[0]-z)+ str(z_flag) +'.png'), img_4)
                os.remove(os.path.join(nodule_play_2D_path, csv_item[0], 'gt_{}.png'.format(shape[0]-z)))
            else:
                cv2.imwrite(os.path.join(nodule_play_2D_path, csv_item[0], 'pred_{}.png'.format(shape[0]-z)), disp_pixel_val[z])
                # Image._show(Image.fromarray(disp_pixel_val[z]))
                img_2 = cv2.imread(os.path.join(nodule_play_2D_path, csv_item[0], 'pred_{}.png'.format(shape[0]-z)))
                img_2 = cv2.circle(img_2, (int(x), int(y)), diameter, (0, 0, 255))
                img_3_draw = Image.fromarray(img_2)
                draw = ImageDraw.Draw(img_3_draw)
                font = ImageFont.truetype('./simheittf.ttf', 30, encoding='utf-8')#记得复制ttf
                draw.text((0, 0), 'Pixel Coord (' + str(float('%.2f' % x)) + ', ' + str(float('%.2f' % y)) + ')', (0, 0, 255), font=font)
                draw.text((0, 35), 'Pred Prob ' + str(float('%.2f' % (float(csv_item[4]) * 100))) + '%', (0, 0, 255), font=font)
                img_4 = np.array(img_3_draw)
                z_flag = z_list.count(z)+1
                cv2.imwrite(os.path.join(nodule_play_2D_path, csv_item[0], 'pred{}-N'.format(shape[0]-z)+ str(z_flag) +'.png'), img_4)
                os.remove(os.path.join(nodule_play_2D_path, csv_item[0], 'pred_{}.png'.format(shape[0]-z)))
        except:
            #traceback.print_exc()
            pass
#主程序。从这里进入。
if __name__ == "__main__":
    fold = 9
    model = 'res'
    lung_ct_SaveRaw = '/home/wl/raid/luna16/subset'+str(fold)+'/'
    nodule_play_all_path = '/home/wl/raid/LUNA16_nodule_play_2D/'
    if model == 'res':
        nodule_play_2D_path = nodule_play_all_path + 'res/'
        pred_csv_file_path = '/ssd/wl/DeepLung/detector/results/res18/test'+str(fold)+'/bbox/predanno-1.5_res.csv'
    else:
        nodule_play_2D_path = nodule_play_all_path + str(model)+'/'
        pred_csv_file_path = '/ssd/wl/DeepLung/detector/results/dpn3d26/test'+str(fold)+'/bbox/predanno-1.5_dpn.csv'
    gt_csv_file_path = '/ssd/wl/DeepLung/evaluationScript/annotations/annotations.csv'
    LUNA16_nodule_play(nodule_play_2D_path, lung_ct_SaveRaw, gt_csv_file_path, gt_pred_flag=True)
    LUNA16_nodule_play(nodule_play_2D_path, lung_ct_SaveRaw, pred_csv_file_path, gt_pred_flag=False)
