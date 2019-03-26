#coding:utf-8
from tkinter import *
import tkinter as tk
import tkinter.filedialog
import cv2
from PIL import Image,ImageTk
import matplotlib.image as mpimg
import os
import numpy as np
import nibabel as nib
from tkinter import IntVar
import matlab.engine
from scipy import misc
import tkinter.messagebox
import time

#建立一个主窗口，窗口上的控件循环显示
window = tk.Tk()
window.title('PET图像分割工具')
window.geometry('1150x1000')

##放置一张背景图片
'''
canvas_bg = Canvas(window,bd=0,height=942,width=896)
canvas_bg.place(x=1000,y=20,anchor='nw')
file_name = ImageTk.PhotoImage(Image.open('./2.jpg'))
canvas_bg.image = file_name  # <--- keep reference of your image
canvas_bg.create_image(0,0,anchor='nw',image=file_name)
'''

########——————————————————————————主窗口的选择打开一个NIfTY文件     （   选择文件     按钮）————————————————————————######
# ##定义 打开 按钮，将选择一个NIfTY文件。保存给变量 nii_file
def select_file():
    global nii_file
    nii_file = tk.filedialog.askopenfilename(parent=window,initialdir='C:/',title='请选择一个NIfTY文件')
    if nii_file != '':
        lb.config(text = "您选择的文件是：" + nii_file)
    else:
        lb.config(text = "您没有选择任何文件")

lb = tk.Label(window,text="您还没有选择文件！",font=("Times", 14),bg='gray',height=1,justify=LEFT)
lb.place(x=1150,y=120,anchor='nw')
btn = tk.Button(window,text = "选择文件 (NIfTY)",command = select_file,width = 16,height=1)
btn.place(x = 1000,y = 120,anchor='nw')

###在主窗口的左边，显示四张图片；在主窗口的右边，显示文字信息和参数设置
tk.Label(window, text="备注：第一行分别为原始图像和分割结果；第二行分别为Top图像和自定义的Top%图像",bg='Ivory',
         font=('Times',14),width=48,height=2,wraplength=400,justify=LEFT).place(x=1000, y=20, anchor='nw')

###——————————————输入i的值，显示原始的第i张切片——————————————————
e = tk.Entry(window)
e.place(x=1150,y=280,height=30,width=50,anchor='nw')
###————————————————————生成原始的切片图像并保存到磁盘中    (选择/生成  按钮)    ————————————————————————————
global var
global nii_array
def Generate_i():
    global var
    global nii_array
    var = e.get()
    #####——————保存图像的同时，将切片的序列号  i    保存到txt文本中
    with open(r'C:\Users\XML\PycharmProjects\DeepLearning\Tkinter\test/myfile.txt','w') as f:
        f.write(var)
    var = int(var)
    data = nib.load(nii_file)
    nii_array = data.get_data()
    save_path = os.path.join(r'C:\Users\XML\PycharmProjects\DeepLearning\Tkinter\test\image1/P1-{}.png'.format(var))
    max_SUV = np.max(nii_array)
    nii_array[nii_array > (0.25*max_SUV)] = (0.25 * max_SUV)
    image_array_single = nii_array[:,:,var-1]
    image_array_single = np.rot90(image_array_single,1)
    image_array_single = cv2.resize(image_array_single,(512,512),interpolation=cv2.INTER_CUBIC)
    image_array_single = image_array_single[128:384,128:384]
    mpimg.imsave(save_path,image_array_single,cmap='gray_r')
b1 = tk.Button(window,text='选择第 i 张切片:',width=15,height=1,command=Generate_i)
b1.place(x=1000,y=280,anchor='nw')

####——————————————————————显示该病人的切片总数——————————————————————————
global count
count = StringVar()
count.set('请选择NIfTY后查看切片数量！')
# count.set('选择文件后确定切片总数！')
def count_slice():
    global nii_file
    data = nib.load(nii_file)
    array = data.get_data()
    data_z = array.shape[2]
    count.set('切片总数量：'+str(data_z))
b4 = tk.Button(window,text='查看切片总数:',width=15,height=1,command=count_slice)
b4.place(x=1000,y=200,anchor='nw')
lb4 = tk.Label(window,textvariable=count ,bg='Linen',font=('Arial',14),width=30,height=1).place(x=1150, y=200, anchor='nw')

#########————————————————————————定义四个canvas,显示四张图片————————————————
canvas_base = tk.Canvas(window,bg='black',height=990,width=990)
canvas_base.place(x=0,y=0,anchor='nw')
canvas1 = tk.Canvas(window,bg='gray',height=450,width=450)
canvas1.place(x=20,y=20,anchor='nw')
canvas2 = tk.Canvas(window,bg='Gray',height=450,width=450)
canvas2.place(x=512,y=20)
canvas3 = tk.Canvas(window,bg='Gray',height=450,width=450)
canvas3.place(x=512,y=512)
canvas4 = tk.Canvas(window,bg='Gray',height=450,width=450)
canvas4.place(x=20,y=512)

canvas_line = tk.Canvas(window,bg='white',height=40,width=1000)
canvas_line.place(x=992,y=470)
########################################################################################################################
##————————————————————选择查看原始切片图像，进行分割部分——————————————————————
global img1                      ##定义图像的全局变量
#####——————————————查看原始图像 （查看第i张切片）——————————————————
def show_Img():
    global img1
    img1 = os.path.join(r'C:\Users\XML\PycharmProjects\DeepLearning\Tkinter\test/image1/P1-{}.png'.format(var))
    filename1 = ImageTk.PhotoImage(Image.open(img1))
    canvas1.image = filename1
    canvas1.create_image(100,100,anchor='nw',image=filename1)
b3 = tk.Button(window,text='查看第 i 张切片',command=show_Img,width=15,height=1)
b3.place(x=1000,y=360,anchor='nw')
######——————————————————分割第 i 张切片———————————————————————————————
def seg_Img():
    eng = matlab.engine.start_matlab()
    t_start = time.clock()
    eng.demo_LRWSuperpixel(nargout=0)
    t_end = time.clock()
    tk.messagebox.showinfo(title='分割时间',message='分割耗时'+ str(t_end - t_start) + '秒')
b5 = tk.Button(window,text='开始分割',command=seg_Img,width=15,height=1)
b5.place(x=1250,y=630,anchor='nw')

####————————————————————查看分割结果————————————————————————————————
global img2
def show_SegImg():
    global img2
    img2 = os.path.join(r'C:\Users\XML\PycharmProjects\DeepLearning\Tkinter\test/image2/result_PET_{}.bmp'.format(var))
    filename2 = ImageTk.PhotoImage(Image.open(img2))
    canvas2.image = filename2
    canvas2.create_image(100,100,anchor='nw',image=filename2)
b6 = tk.Button(window,text='查看分割结果 (i):',command=show_SegImg,width=15,height=1)
b6.place(x=1400,y=630,anchor='nw')

###——————————————————————设置迭代的次数，默认为0次————————————————————————
ee = tk.Entry(window)
ee.place(x=1150,y=630,height=30,width=50,anchor='nw')
l3 = tk.Label(window,bg='gray',width=24,text="您还没有选择迭代次数！",font=('Times',14))
l3.place(x=1000,y=550,anchor='nw')
global iteration
def print_iteration():
    global iteration
    iteration = ee.get()
    l3.config(text='已选择迭代次数: '+iteration+' 次')
    #####——————将输入的迭代次数  保存到txt文本中
    with open(r'C:\Users\XML\PycharmProjects\DeepLearning\Tkinter\test/iteration.txt','w') as f:
        f.write(iteration)
b11 = tk.Button(window,text='选择迭代次数:',width=15,height=1,command=print_iteration)
b11.place(x=1000,y=630,anchor='nw')

#####————————————————————————使用一个输入框dd，设置百分比的值——————————————————
dd = tk.Entry(window)
dd.place(x=1150,y=710,height=30,width=50,anchor='nw')
l = tk.Label(window,bg='gray',width=30,text='您还没有选择阈值！(建议10-40之间)',font=('Times',14))
l.place(x=1250,y=710,anchor='nw')
global var_seclection
def print_seclection():
    global var_seclection
    var_seclection = dd.get()
    l.config(text='你已经选择了:'+var_seclection+'%')
    #####——————将输入的阈值  保存到txt文本中
    with open(r'C:\Users\XML\PycharmProjects\DeepLearning\Tkinter\test/selection.txt','w') as f:
        f.write(var_seclection)
b7 = tk.Button(window,text='选择你的阈值:(%)',width=15,height=1,command=print_seclection)
b7.place(x=1000,y=710,anchor='nw')

#####——————————————————展示两个Tumor的RGB图像———————————————————————————————
global img3                      ##定义图像的全局变量
global img4
#####——————————————查看原始图像 （查看第i张切片）——————————————————
def ShowTumor():
    global nii_array
    file_object = open(r'C:\Users\XML\PycharmProjects\DeepLearning\Tkinter\test/myfile.txt')
    file_content = file_object.read()
    xx = int(file_content)

    result_label_img_path = r'C:\Users\XML\PycharmProjects\DeepLearning\Tkinter\test\used_image/result_label_img_{}.bmp'.format(
        xx)
    result_PET1_path = r'C:\Users\XML\PycharmProjects\DeepLearning\Tkinter\test\used_image/result_PET1_{}.bmp'.format(
        xx)

    result_label_image = mpimg.imread(result_label_img_path)  # 获取label(1-200)的label 矩阵
    seg_PET1_image = mpimg.imread(result_PET1_path)  # 获取分割图像的矩阵
    SUV_array = nii_array[:, :, xx - 1]

    SUV_array = np.rot90(SUV_array, 1)
    SUV_array = cv2.resize(SUV_array, (512, 512), interpolation=cv2.INTER_CUBIC)
    SUV_array = SUV_array[128:384, 128:384]
    SUV_array[SUV_array < 0] = 0

    max_label = np.max(result_label_image)  # 获取lab的最大值，就是超像素的数量
    count_label = np.zeros(max_label + 1)  # 保存每个label的像素的数目
    sum_SUV = np.zeros(max_label + 1)  # 保存每个label的超像素的灰度值的和
    mean_SUV = np.zeros(max_label + 1)  # 创建一个数组，保存每个超像素的灰度值的均值(多了一个元)
    ##获取1-max_label的标签的对应的元素的坐标：在512*512的矩阵中找
    ##得到的x[i],y[i]为对应了label == i 的元的横坐标和纵坐标
    for ii in range(1, (max_label + 1)):
        bool_label_img = (result_label_image == ii)
        count_label[ii] = np.count_nonzero(bool_label_img)  # 得到label=i的元素的数量,统计结果存储到一维数组中
        ##得到每个label的全部元素的SUV值的和
        [x, y] = np.where(result_label_image == ii)  # 得到的x,y分别为两个一维矩阵，（x[j],y[j]）为第j个label值=i的元素的横纵坐标
        sum_SUV[ii] = 0
        for j in range(0, len(x)):
            sum_SUV[ii] = sum_SUV[ii] + SUV_array[x[j], y[j]]

        mean_SUV[ii] = sum_SUV[ii] / count_label[ii]  ##得到每个超像素的平均SUV值

    ###——————————————————保存一个病变可能性最大的区域————————————————————————
    # ##得到SUV(平均)的最大值，得到对应的label,得到这个label的全部元素的坐标。显示这个区域：
    SUV_aver_max = np.max(mean_SUV)
    index_label = np.where(mean_SUV == SUV_aver_max)
    index_label = list(index_label)
    index_label = index_label[0]
    ##显示这个最大平均SUV值的区域
    Tumor_image = (result_label_image == index_label)  # 只有label值为index_label的值被保存，得到的是一个布尔矩阵。布尔矩阵与seg图像对应元相乘
    Tumor_image = Tumor_image * seg_PET1_image
    Tumor_image[Tumor_image == 0] = 255  # 将背景转化为白色
    misc.imsave(r'C:\Users\XML\PycharmProjects\DeepLearning\Tkinter\test\image3/TumorMP-{}.png'.format(xx), Tumor_image)

    ####——————————————————将SUV（max）*0.9  到 SUV(max)的区域保存出来
    file_object2 = open(r'C:\Users\XML\PycharmProjects\DeepLearning\Tkinter\test/selection.txt')
    file_content_selection = file_object2.read()
    file_content_selection = int(file_content_selection)
    index_sec_added_label = np.where(mean_SUV > (SUV_aver_max * (100 - file_content_selection) * 0.01))
    index_sec_added_label = np.array(index_sec_added_label)

    num = len(index_sec_added_label[0])
    Tumor_image_sec = np.zeros(Tumor_image.shape)
    for kk in range(0, num):
        Tumor_image_sec = Tumor_image_sec + (result_label_image == index_sec_added_label[0, kk])  ##一次循环加入一个超像素
    Tumor_image_sec = Tumor_image_sec * seg_PET1_image
    Tumor_image_sec[Tumor_image_sec == 0] = 255
    misc.imsave(r'C:\Users\XML\PycharmProjects\DeepLearning\Tkinter\test\image4/TumorPercent-{}.png'.format(xx),
                Tumor_image_sec)

    file_object = open(r'C:\Users\XML\PycharmProjects\DeepLearning\Tkinter\test/myfile.txt')
    file_content = file_object.read()
    ii = int(file_content)

    img = cv2.imread(os.path.join(
        r'C:\Users\XML\PycharmProjects\DeepLearning\Tkinter\test\used_image/result_gray_img_{}.bmp'.format(ii)))
    tumor_Top = cv2.imread(
        os.path.join(r'C:\Users\XML\PycharmProjects\DeepLearning\Tkinter\test\image3/TumorMP-{}.png'.format(ii)))
    tumor_Top = tumor_Top[:, :, 0]

    [x, y] = np.where(tumor_Top != 255)
    for i in range(0, len(x)):
        img[x[i], y[i], 1] = 255
        img[x[i], y[i], 0] = 255
    cv2.imwrite(
        os.path.join(r'C:\Users\XML\PycharmProjects\DeepLearning\Tkinter\test\image3/', 'Top-{}.bmp'.format(ii)), img)

    ###—————————————————保存Tumor的Top 10%的全部超像素—————————————————————————————
    img = cv2.imread(os.path.join(
        r'C:\Users\XML\PycharmProjects\DeepLearning\Tkinter\test\used_image/result_gray_img_{}.bmp'.format(ii)))
    tumor_Top_10 = cv2.imread(
        os.path.join(r'C:\Users\XML\PycharmProjects\DeepLearning\Tkinter\test\image4/TumorPercent-{}.png'.format(ii)))
    tumor_Top_10 = tumor_Top_10[:, :, 0]
    [xx, yy] = np.where(tumor_Top_10 != 255)
    for jj in range(0, len(xx)):
        img[xx[jj], yy[jj], 1] = 255
        img[xx[jj], yy[jj], 0] = 255
    cv2.imwrite(
        os.path.join(r'C:\Users\XML\PycharmProjects\DeepLearning\Tkinter\test\image4/', 'TopPer-{}.bmp'.format(ii)),
        img)


    global img3
    global img4
    img3 = os.path.join(r'C:\Users\XML\PycharmProjects\DeepLearning\Tkinter\test\image4/TopPer-{}.bmp'.format(var))
    img4 = os.path.join(r'C:\Users\XML\PycharmProjects\DeepLearning\Tkinter\test\image3/Top-{}.bmp'.format(var))
    filename3 = ImageTk.PhotoImage(Image.open(img3))
    filename4 = ImageTk.PhotoImage(Image.open(img4))
    canvas3.image = filename3
    canvas4.image = filename4
    canvas3.create_image(100,100,anchor='nw',image=filename3)
    canvas4.create_image(100, 100, anchor='nw', image=filename4)
b10 = tk.Button(window,text='查看目标区域',width=15,height=1,command=ShowTumor)
b10.place(x=1000,y=790,anchor='nw')

window.mainloop()