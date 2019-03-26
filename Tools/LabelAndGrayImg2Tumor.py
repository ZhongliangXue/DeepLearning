import numpy as np
import matplotlib.image as mpimg
from scipy import misc
import os

for ii in range(4,5):
    result_label_img_path = os.path.join(r'C:\Users\XML\PycharmProjects\DeepLearning\P1/','result_label_img_{}.bmp'.format(ii))
    gray_img_path = os.path.join(r'C:\Users\XML\PycharmProjects\DeepLearning\P1/', 'result_gray_img_{}.bmp'.format(ii))
    result_gray_img_path = os.path.join(r'C:\Users\XML\PycharmProjects\DeepLearning\P1/', 'result_PET1_{}.bmp'.format(ii))
    ##加载label_img 和 gray_img
    label_img = mpimg.imread(result_label_img_path)
    gray_img = mpimg.imread(gray_img_path)
    result_gray_img = mpimg.imread(result_gray_img_path)

    # plt.imshow(gray_img,cmap='gray')
    # plt.axis('off')
    # plt.show()

    ##——————————————————————————————————————————————————————
    max_label = np.max(label_img)
    count_label = np.zeros(max_label+1)                   #保存每个label的像素的数目
    sum_gray = np.zeros(max_label+1)                      #保存每个label的超像素的灰度值的和
    mean_gray = np.zeros(max_label+1)                     #创建一个数组，保存每个超像素的灰度值的均值(多了一个元)
    ##获取1-max_label的标签的对应的元素的坐标：在494*628的矩阵中找
    ##得到的x[i],y[i]为对应了label == i 的元的横坐标和纵坐标
    for i in range(1,(max_label+1)):
        bool_label_img = (label_img == i)
        count_label[i] = np.count_nonzero(bool_label_img)  #得到label=i的元素的数量,统计结果存储到一维数组中

    ##——————————————————————————————————————————————————————
    ##得到了每个label的全部元素的灰度值的和
        [x,y] = np.where(label_img == i)
        sum_gray[i] = 0
        for j in range(0,len(x)):
            sum_gray[i] = sum_gray[i] + gray_img[x[j],y[j]]

    ##得到每个label区域的元素的平均值
        mean_gray[i] = sum_gray[i]/count_label[i]

    ##——————————————————————————————————————————————————————
    ##输出mean_gray[]的最小的三个值和对应的label(位置索引)，除去首位的0
    mean_gray[0] = 255
    # print(np.min(mean_gray),'最小值的label:',np.where(mean_gray == np.min(mean_gray)))
    index_min = np.where(mean_gray == np.min(mean_gray))
    index_min = list(index_min)
    index_min = index_min[0]
    index_min = index_min[0]

    ##均值倒数第二小的超像素label
    mean_gray[index_min] = 255
    index_min_1 = np.where(mean_gray == np.min(mean_gray))
    index_min_1 = list(index_min_1)
    index_min_1 = index_min_1[0]
    index_min_1 = index_min_1[0]

    ##均值倒数第三小的超像素label
    mean_gray[index_min_1] = 255
    index_min_2 = np.where(mean_gray == np.min(mean_gray))
    index_min_2 = list(index_min_2)
    index_min_2 = index_min_2[0]
    index_min_2 = index_min_2[0]

    ##均值倒数第四小的超像素label
    mean_gray[index_min_2] = 255
    index_min_3 = np.where(mean_gray == np.min(mean_gray))
    index_min_3 = list(index_min_3)
    index_min_3 = index_min_3[0]
    index_min_3 = index_min_3[0]

    ##均值倒数第五小的超像素label
    mean_gray[index_min_3] = 255
    index_min_4 = np.where(mean_gray == np.min(mean_gray))
    index_min_4 = list(index_min_4)
    index_min_4 = index_min_4[0]
    index_min_4 = index_min_4[0]

    ##均值倒数第六小的超像素label
    mean_gray[index_min_4] = 255
    index_min_5 = np.where(mean_gray == np.min(mean_gray))
    index_min_5 = list(index_min_5)
    index_min_5 = index_min_5[0]
    index_min_5 = index_min_5[0]
    ##——————————————————————————————————————————————
    #将超像素均值最小的一、二、三、四、五、六个保存出来
    label_img_Tumor = label_img
    label_img_Tumor_0 = (label_img_Tumor == index_min)
    label_img_Tumor_1 = (label_img_Tumor == index_min_1)
    label_img_Tumor_2 = (label_img_Tumor == index_min_2)
    label_img_Tumor_3 = (label_img_Tumor == index_min_3)
    label_img_Tumor_4 = (label_img_Tumor == index_min_4)
    label_img_Tumor_5 = (label_img_Tumor == index_min_5)

    ##———————————————保存轮廓图像和对应的灰度图————————————————————
    result_image_path = r'C:\Users\XML\PycharmProjects\DeepLearning\P1_result/'
    # 调整得到1个超像素的联合区域图像，并保存（轮廓图）
    label_img_Tumor = label_img_Tumor_0
    label_img_Tumor = np.uint8(label_img_Tumor)
    label_img_Tumor[label_img_Tumor == 1] = 255
    misc.imsave(os.path.join(result_image_path,'SP_0_{}.png'.format(ii)),label_img_Tumor)
    # 得到1个超像素的联合区域图像，并保存（灰度图）
    [a,b] = np.where(label_img_Tumor == 255)
    label_img_Tumor[label_img_Tumor != 255] = 255
    for i in range(0,len(a)):
        label_img_Tumor[a[i],b[i]] = result_gray_img[a[i],b[i]]   #把轮廓中对应的灰度图的值保存出来
    misc.imsave(os.path.join(result_image_path,'SP_0_gray_{}.png'.format(ii)),label_img_Tumor)

    # 调整得到2个超像素的联合区域图像，并保存（轮廓）
    label_img_Tumor = label_img_Tumor_0 + label_img_Tumor_1
    label_img_Tumor = np.uint8(label_img_Tumor)
    label_img_Tumor[label_img_Tumor == 1] = 255
    misc.imsave(os.path.join(result_image_path,'SP_1_{}.png'.format(ii)),label_img_Tumor)
    # 得到2个超像素的联合区域图像，并保存（灰度图）
    [a,b] = np.where(label_img_Tumor == 255)
    label_img_Tumor[label_img_Tumor != 255] = 255
    for i in range(0,len(a)):
        label_img_Tumor[a[i],b[i]] = result_gray_img[a[i],b[i]]   #把轮廓中对应的灰度图的值保存出来
    misc.imsave(os.path.join(result_image_path,'SP_1_gray_{}.png'.format(ii)),label_img_Tumor)

    # 调整得到3个超像素的联合区域图像，并保存（轮廓）
    label_img_Tumor = label_img_Tumor_0 + label_img_Tumor_1 + label_img_Tumor_2
    label_img_Tumor = np.uint8(label_img_Tumor)
    label_img_Tumor[label_img_Tumor == 1] = 255
    misc.imsave(os.path.join(result_image_path,'SP_2_{}.png'.format(ii)),label_img_Tumor)
    # 得到3个超像素的联合区域图像，并保存（灰度图）
    [a,b] = np.where(label_img_Tumor == 255)
    label_img_Tumor[label_img_Tumor != 255] = 255
    for i in range(0,len(a)):
        label_img_Tumor[a[i],b[i]] = result_gray_img[a[i],b[i]]   #把轮廓中对应的灰度图的值保存出来
    misc.imsave(os.path.join(result_image_path,'SP_2_gray_{}.png'.format(ii)),label_img_Tumor)

    # 调整得到4个超像素的联合区域图像，并保存（轮廓）
    label_img_Tumor = label_img_Tumor_0 + label_img_Tumor_1 + label_img_Tumor_2 + label_img_Tumor_3
    label_img_Tumor = np.uint8(label_img_Tumor)
    label_img_Tumor[label_img_Tumor == 1] = 255
    misc.imsave(os.path.join(result_image_path,'SP_3_{}.png'.format(ii)),label_img_Tumor)
    # 得到4个超像素的联合区域图像，并保存（灰度图）
    [a,b] = np.where(label_img_Tumor == 255)
    label_img_Tumor[label_img_Tumor != 255] = 255
    for i in range(0,len(a)):
        label_img_Tumor[a[i],b[i]] = result_gray_img[a[i],b[i]]   #把轮廓中对应的灰度图的值保存出来
    misc.imsave(os.path.join(result_image_path,'SP_3_gray_{}.png'.format(ii)),label_img_Tumor)

    # 调整得到5个超像素的联合区域图像，并保存（轮廓）
    label_img_Tumor = label_img_Tumor_0 + label_img_Tumor_1 + label_img_Tumor_2 + label_img_Tumor_3 + label_img_Tumor_4
    label_img_Tumor = np.uint8(label_img_Tumor)
    label_img_Tumor[label_img_Tumor == 1] = 255
    misc.imsave(os.path.join(result_image_path,'SP_4_{}.png'.format(ii)),label_img_Tumor)
    # 得到5个超像素的联合区域图像，并保存（灰度图）
    [a,b] = np.where(label_img_Tumor == 255)
    label_img_Tumor[label_img_Tumor != 255] = 255
    for i in range(0,len(a)):
        label_img_Tumor[a[i],b[i]] = result_gray_img[a[i],b[i]]   #把轮廓中对应的灰度图的值保存出来
    misc.imsave(os.path.join(result_image_path,'SP_4_gray_{}.png'.format(ii)),label_img_Tumor)

    # 调整得到6个超像素的联合区域图像，并保存(轮廓)
    label_img_Tumor = label_img_Tumor_0 + label_img_Tumor_1 + label_img_Tumor_2 + label_img_Tumor_3 + label_img_Tumor_4 + label_img_Tumor_5
    label_img_Tumor = np.uint8(label_img_Tumor)
    label_img_Tumor[label_img_Tumor == 1] = 255
    misc.imsave(os.path.join(result_image_path,'SP_5_{}.png'.format(ii)),label_img_Tumor)
    # 得到6个超像素的联合区域图像，并保存（灰度图）
    [a,b] = np.where(label_img_Tumor == 255)
    label_img_Tumor[label_img_Tumor != 255] = 255
    for i in range(0,len(a)):
        label_img_Tumor[a[i],b[i]] = result_gray_img[a[i],b[i]]   #把轮廓中对应的灰度图的值保存出来
    misc.imsave(os.path.join(result_image_path,'SP_5_gray_{}.png'.format(ii)),label_img_Tumor)

