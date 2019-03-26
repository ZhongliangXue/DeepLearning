#coding:utf-8
import tkinter as tk
import cv2
from tkinter import filedialog
from PIL import Image, ImageTk

##界面上的控件开始循环显示
window = tk.Tk()
window.title('PET图像分割工具')
window.geometry('800x1200')
# tk.Label(window,text='工具窗口',font=('Arial',12)).pack()

##建立一个主frame，再在上面建立4个子Frame，分别显示4张图片结果:子Frame的位置分别在上下左右
frm = tk.Frame(window)
frm.pack()

############################################

def do_job():
    global counter
    l.config(text='do ' + str(counter))
    counter += 1
# 第5步，创建一个菜单栏，这里我们可以把他理解成一个容器，在窗口的上方
menubar = tk.Menu(window)

# 第6步，创建一个File菜单项（默认不下拉，下拉内容包括New，Open，Save，Exit功能项）
filemenu = tk.Menu(menubar, tearoff=0)
# 将上面定义的空菜单命名为File，放在菜单栏中，就是装入那个容器中
menubar.add_cascade(label='选择', menu=filemenu)

# 在File中加入New、Open、Save等小菜单，即我们平时看到的下拉菜单，每一个小菜单对应命令操作。
filemenu.add_command(label='打开DICOM序列', command=do_job)
filemenu.add_command(label='打开NIfTy', command=do_job)
filemenu.add_command(label='打开图片', command=do_job)
filemenu.add_separator()  # 添加一条分隔线
filemenu.add_command(label='退出', command=window.quit)  # 用tkinter里面自带的quit()函数

# 第7步，创建一个Edit菜单项（默认不下拉，下拉内容包括Cut，Copy，Paste功能项）
editmenu = tk.Menu(menubar, tearoff=0)
# 将上面定义的空菜单命名为 Edit，放在菜单栏中，就是装入那个容器中

# 同样的在 Edit 中加入Cut、Copy、Paste等小命令功能单元，如果点击这些单元, 就会触发do_job的功能
editmenu.add_command(label='开始分割', command=do_job)
editmenu.add_command(label='暂停', command=do_job)
editmenu.add_command(label='取消', command=do_job)


# 第11步，创建菜单栏完成后，配置让菜单栏menubar显示出来
window.config(menu=menubar)






###############################################
frm_l = tk.Frame(frm)
frm_r = tk.Frame(frm)
frm_top = tk.Frame(frm)
frm_bottom = tk.Frame(frm)

frm_l.pack(side='left',anchor='n')
frm_r.pack(side='right',anchor='s')
frm_top.pack(side='top',anchor='w')
frm_bottom.pack(side='bottom',anchor='n')


##为每一个子Frame放置自己的控件
tk.Label(frm_l,text='PET原始图像',bg='yellow',font=('Arial',12),width=15,height=1).pack(side='top')
tk.Label(frm_r,text='病人编号：',bg='white',font=('Arial',12),width=15,height=1).pack(side='top')
tk.Label(frm_r,text='切片编号：',bg='white',font=('Arial',12),width=15,height=1).pack(side='top')
tk.Label(frm_r,text='PET分割结果',bg='white',font=('Arial',12),width=15,height=1).pack(side='bottom')
tk.Label(frm_top,text='最大SUV的一个超像素',bg='pink',font=('Arial',12),width=20,height=1).pack(side='top')
tk.Label(frm_bottom,text='自定义范围结果',bg='pink',font=('Arial',12),width=15,height=1).pack(side='bottom')

l = tk.Label(frm_r,bg='yellow',width=20,text='默认的参数为10',font=('Arial',12))
l.pack(side='bottom')
##显示最后一个窗口中的用户选择的范围（%）,这个文本只能显示在label等控件里面，不可以直接显示在Frame中。
def print_selection(v):
    l.config(text='你已经选择了'+ v)
tk.Scale(frm_l,label='[参数设置](%)',from_=10,to=40,orient=tk.HORIZONTAL,length=300,showvalue=1,tickinterval=10,resolution=0.01,command=print_selection).pack(side='bottom',anchor='n')
tk.Button(frm_l,text='开始分割').pack(side='bottom',anchor='s')

###设置好参数之后，显示四个窗口中的图片
##第一个图片
canvas_l = tk.Canvas(frm_l,bg='white',height=512,width=512)
canvas_l.pack()
filename_l = ImageTk.PhotoImage(Image.open('P1-128.png'))
canvas_l.image = filename_l
canvas_l.create_image(0,0,anchor='nw',image=filename_l)

canvas_r = tk.Canvas(frm_r,bg='white',height=512,width=512)
canvas_r.pack()
filename_r = ImageTk.PhotoImage(Image.open('result_PET_128.bmp'))
canvas_r.image = filename_r
canvas_r.create_image(0,0,anchor='nw',image=filename_r)

canvas_top = tk.Canvas(frm_top,bg='white',height=512,width=512)
canvas_top.pack()
filename_top = ImageTk.PhotoImage(Image.open('Top-128.bmp'))
canvas_top.image = filename_top
canvas_top.create_image(0,0,anchor='nw',image=filename_top)

canvas_bottom = tk.Canvas(frm_bottom,bg='white',height=512,width=512)
canvas_bottom.pack()
filename_bottom = ImageTk.PhotoImage(Image.open('Top10-128.bmp'))
canvas_bottom.image = filename_top
canvas_bottom.create_image(0,0,anchor='nw',image=filename_bottom)



window.mainloop()
