import cv2
import numpy as np
import os

###——————————————————保存Tumor的Top的一个超像素——————————————————————————————
file_object = open(r'C:\Users\XML\PycharmProjects\DeepLearning\Tkinter\test/myfile.txt')
file_content = file_object.read()
ii = int(file_content)

img = cv2.imread(os.path.join(r'C:\Users\XML\PycharmProjects\DeepLearning\Tkinter\test\used_image/result_gray_img_{}.bmp'.format(ii)))
tumor_Top = cv2.imread(os.path.join(r'C:\Users\XML\PycharmProjects\DeepLearning\Tkinter\test\image3/TumorMP-{}.png'.format(ii)))
tumor_Top = tumor_Top[:,:,0]

[x,y]= np.where(tumor_Top != 255)
for i in range(0,len(x)):
    img[x[i],y[i],1] = 255
    img[x[i], y[i],0] = 255
cv2.imwrite(os.path.join(r'C:\Users\XML\PycharmProjects\DeepLearning\Tkinter\test\image3/','Top-{}.bmp'.format(ii)),img)

###—————————————————保存Tumor的Top 10%的全部超像素—————————————————————————————
img = cv2.imread(os.path.join(r'C:\Users\XML\PycharmProjects\DeepLearning\Tkinter\test\used_image/result_gray_img_{}.bmp'.format(ii)))
tumor_Top_10 = cv2.imread(os.path.join(r'C:\Users\XML\PycharmProjects\DeepLearning\Tkinter\test\image4/TumorPercent-{}.png'.format(ii)))
tumor_Top_10 = tumor_Top_10[:, :, 0]
[xx,yy] = np.where(tumor_Top_10 != 255)
for jj in range(0,len(xx)):
    img[xx[jj], yy[jj], 1] = 255
    img[xx[jj], yy[jj], 0] = 255
cv2.imwrite(os.path.join(r'C:\Users\XML\PycharmProjects\DeepLearning\Tkinter\test\image4/', 'TopPer-{}.bmp'.format(ii)), img)
