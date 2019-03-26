from __future__ import print_function

import SimpleITK as sitk
import sys,os,time

if len(sys.argv) < 3:
    print('Usage: DicomSeriesReader <input_directory> <output_file>')
    sys.exit(1)

### 读取原始的序列，首先使用读取函数  获得文件名

data_directory = sys.argv[1]
series_IDs = sitk.ImageSeriesReader.GetGDCMSeriesIDs(data_directory)
if not series_IDs:
    print('ERROR: given directory \''+data_directory+'\'does not contain a DICM series.')
    sys.exit(1)
series_file_name = sitk.ImageSeriesReader.GetGDCMSeriesFileNames(data_directory,series_IDs[0])

series_reader = sitk.ImageSeriesReader()
series_reader.SetFileNames(series_file_name)

### 确保读取器加载了全部的DICOM标签 （公有的 + 私有的）：
### 通过缺省 没有加载的标签 （保存时间）
### 通过缺省 ，如果标签加载了，但是私有标签没有加载
### 私有部分。

series_reader.MetaDataDictionaryArrayUpdateOn()
series_reader.LoadPrivateTagsOn()
image3D = series_reader.Execute()

### ——————————————————“修改图像”，使得图像难以辨认——————————————————
filtered_image = sitk.DiscreteGaussian(image3D)

### 将一个3D图像写成一个DICOM序列
### 重点：当修改一个原始图像的时候，很多DICOM tags 需要被修改。这是一个易损的操作，需要了解DICOM文件：
### http://gdcm.sourceforge.net/wiki/index.php/Writing_DICOM  （可以修改别的tags内容）

writer = sitk.ImageFileWriter()
### ——————————注释————————————————————————————————————————
writer.KeepOriginalImageUIDOn()

#### 复制相关的tags 从原始的中间数据 （私有tags也是可以获得的）
tags_to_copy = ["0010|0010", # Patient Name
                "0010|0020", # Patient ID
                "0010|0030", # Patient Birth Date
                "0020|000D", # Study Instance UID, for machine consumption
                "0020|0010", # Study ID, for human consumption
                "0008|0020", # Study Date
                "0008|0030", # Study Time
                "0008|0050", # Accession Number
                "0008|0060"  # Modality
]

modification_time = time.strftime("%H%M%S")
modification_date = time.strftime("%Y%m%d")

### 复制一些tags 添加相关的标签来表明修改的内容
### 使用 一个‘.’来分开   使用日期和时间 创建一个独特的序列ID

direction =filtered_image.GetDirection()
series_tag_values = [(k, series_reader.GetMetaData(0,k)) for k in tags_to_copy if series_reader.HasMetaDataKey(0,k)] + \
                 [("0008|0031",modification_time), # Series Time
                  ("0008|0021",modification_date), # Series Date
                  ("0008|0008","DERIVED\\SECONDARY"), # Image Type
                  ("0020|000e", "1.2.826.0.1.3680043.2.1125."+modification_date+".1"+modification_time), # Series Instance UID
                  ("0020|0037", '\\'.join(map(str, (direction[0], direction[3], direction[6],# Image Orientation (Patient)
                                                    direction[1],direction[4],direction[7])))),
                  ("0008|103e", series_reader.GetMetaData(0,"0008|103e") + " Processed-SimpleITK")] # Series Description

for i in range(filtered_image.GetDepth()):
    image_slice = filtered_image[:,:,i]
    ## Tags -- 切片序列
    for tag,value in series_tag_values:
        image_slice.SetMetaData(tag,value)

    # Slice specific tags.
    image_slice.SetMetaData("0008|0012", time.strftime("%Y%m%d"))  # Instance Creation Date
    image_slice.SetMetaData("0008|0013", time.strftime("%H%M%S"))  # Instance Creation Time
    image_slice.SetMetaData("0020|0032", '\\'.join(
        map(str, filtered_image.TransformIndexToPhysicalPoint((0, 0, i)))))  # Image Position (Patient)
    image_slice.SetMetaData("0020|0013", str(i))  # Instance Number

    ### 写到输出目录  添加强制的dcm扩展，强制写成DICOM格式
    writer.SetFileName(os.path.join(sys.argv[2],str[i]+'.dcm'))
    writer.Execute(image_slice)

sys.exit(0)


























