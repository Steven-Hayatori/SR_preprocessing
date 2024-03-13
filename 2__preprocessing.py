introduction = str("本文件主要完成四个任务：\n\t任务一：将1origin文件夹中图片改变像素放入2reshape文件夹\n\t任务二：将2reshape文件夹中图片做扩张数据集处理（具体处理方法见expand函数）\n\t任务三：对扩张后的STED图像做HC处理\n\t任务四：对扩张后的数据集做清洗")

import os
import cv2
import numpy as np
import shutil

import datetime


# 基本参数
folder_origin = r'./1origin'
folder_reshape = r'./2reshape'
folder_expand = r'./3expand'
folder_purge = r'./4purge'


# 辅助函数
def create_folder(dir_path):
    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path)
        except OSError as e:
            print(f"创建目录 {dir_path}' 失败：{e}")

def delete_folder(dir_path):
    if os.path.exists(dir_path):
        try:
            for root, dirs, files in os.walk(dir_path, topdown=False):
                for file in files:
                    file_path = os.path.join(root, file)
                    os.remove(file_path)
                for dir_name in dirs:
                    subdir_path = os.path.join(root, dir_name)
                    shutil.rmtree(subdir_path)
            os.rmdir(dir_path)
        except OSError as e:
            print(f"删除目录 '{dir_path}' 及其子文件夹内所有文件失败：{e}")

def count_files(dir_path):
    try:
        file_count = 0
        for _, _, files in os.walk(dir_path):
            file_count += len(files)
        return file_count
    except Exception as e:
        print(f"统计目录 '{dir_path}' 内的文件数量失败：{e}")

##将index在"list"中的图像筛选出来
def duplicate_from_list(folder_old,folder_new,foldercount,list):
    global count_global
    if foldercount == 2:
        type = ['Confocal','STED']
    elif foldercount == 3:
        types = ['Confocal','STED','STED_HC']
    for type in types:
        dir_old = os.path.join(folder_old,type)
        dir_new = os.path.join(folder_new,type)
        count_temp = 0
        for i in list:
            fullname_old = str(str(i)+'_'+type+'.png')
            fullname_new = str(str(count_temp)+'_'+type+'.png')
            fullpath_old = os.path.join(dir_old,fullname_old)
            fullpath_new = os.path.join(dir_new,fullname_new)
            shutil.copy2(fullpath_old,fullpath_new)
            count_temp += 1
    count_global = count_temp

# 主函数
def folder_preparation():
    delete_folder(folder_reshape)
    delete_folder(folder_expand)
    delete_folder(folder_purge)
    create_folder(os.path.join(folder_reshape,'Confocal'))
    create_folder(os.path.join(folder_reshape,'STED'))
    create_folder(os.path.join(folder_expand,'Confocal'))
    create_folder(os.path.join(folder_expand,'STED'))
    create_folder(os.path.join(folder_expand,'STED_HC'))
    create_folder(os.path.join(folder_purge,'Confocal'))
    create_folder(os.path.join(folder_purge,'STED'))
    create_folder(os.path.join(folder_purge,'STED_HC'))


def RESHAPE(folder_old, folder_new):
    global global_count

    SIZE = 256

    count_temp = 0 
    types = ['Confocal','STED']
    for type in types:
        dir_old = os.path.join(folder_old,type)
        dir_new = os.path.join(folder_new,type)
        for i in range(count_global):
            fullname = str(str(i)+'_'+str(type)+'.png')
            fullpath_old = os.path.join(dir_old,fullname)
            fullpath_new = os.path.join(dir_new,fullname)
            img = cv2.imread(fullpath_old,0)     
            resized_image = cv2.resize(img, (SIZE,SIZE), interpolation=cv2.INTER_AREA)
            cv2.imwrite(fullpath_new,resized_image) 
    global_count = count_temp


## 数据集扩张，包括切割旋转翻转
def EXPAND(folder_old, folder_new):
    global count_global

    # 开关
    DIVISION_CONSTANT = 1 #2的意思是切成2x2
    DO_ROTATION = 1
    DO_OVERTURN = 1

    types = ['Confocal','STED']
    for type in types:
        dir_old = os.path.join(folder_old,type)
        dir_new = os.path.join(folder_new,type)
        count_temp = 0
        for i in range(count_global):
            fullname = str(str(i)+'_'+str(type)+'.png')
            fullpath_old = os.path.join(dir_old,fullname)
            fullpath_new = os.path.join(dir_new,fullname)
            img = cv2.imread(fullpath_old,0)     
            if len(img.shape) == 2:
                height,width = img.shape
            elif len(img.shape) == 3:
                height,width,_ = img.shape
            for j in range(0,DIVISION_CONSTANT):
                for k in range(0,DIVISION_CONSTANT):
                    img_divided = img[j*height//DIVISION_CONSTANT:(j+1)*height//DIVISION_CONSTANT,k*width//DIVISION_CONSTANT:(k+1)*width//DIVISION_CONSTANT]
                    if DO_ROTATION == 1:
                        rotation_list = [0,1,2,3]
                    elif DO_ROTATION == 0:
                        rotation_list = [0]
                    for rotation_counts in rotation_list:
                        angle = rotation_counts*90
                        center = height//(2*DIVISION_CONSTANT),width//(2*DIVISION_CONSTANT)
                        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
                        img_rotated = cv2.warpAffine(img_divided,rotation_matrix,(width//DIVISION_CONSTANT, height//DIVISION_CONSTANT))
                        if DO_OVERTURN == 1:
                            overturn_list = [0,1,2,3]
                        elif DO_OVERTURN == 0:
                            overturn_list = [0]
                        for overturn_counts in overturn_list:
                            if overturn_counts == 0:
                                img_overturned = img_rotated
                            elif overturn_counts == 1:
                                img_overturned = cv2.flip(img_rotated, 0) # 水平翻转
                            elif overturn_counts == 2:
                                img_overturned = cv2.flip(img_rotated, 1) # 垂直翻转
                            elif overturn_counts == 3:
                                img_overturned = cv2.flip(img_rotated, -1) # 水平和垂直翻转    
                            fullpath_new = os.path.join(dir_new,str(count_temp)+'_'+type+'.png')
                            cv2.imwrite(fullpath_new,img_overturned)
                            count_temp += 1
    count_global = count_temp

def HIGH_CONTRAST(folder):
    global count_global
    for i in range(count_global):
        fullname_old = str(str(i)+'_'+'STED'+'.png')
        fullname_new = str(str(i)+'_'+'STED_HC'+'.png')
        fullpath_old = os.path.join(folder,'STED',fullname_old)
        fullpath_new = os.path.join(folder,'STED_HC',fullname_new)
        img_origin = cv2.imread(fullpath_old,0)
        #滤掉30以下像素
        threshold = 30
        img_new = np.zeros_like(img_origin)
        img_new[img_origin>threshold] = img_origin[img_origin>threshold]
        # 进行伽马校正
        gamma = 0.9
        img_HC = np.power(img_new / 255.0, gamma)
        img_HC = np.uint8(img_HC * 255)
        cv2.imwrite(fullpath_new,img_HC)

def PURGE(folder_old, folder_new):
    global count_global
    list_yes = []
    for i in range(count_global):
        fullname = str(str(i)+'_'+'STED_HC'+'.png')
        fullpath_old = os.path.join(folder_old,'STED_HC',fullname)
        img_origin = cv2.imread(fullpath_old,0)
        average_brightness = img_origin.mean()
        if average_brightness > 2:  #0.032  3.75  20.27
            list_yes.append(i)
    duplicate_from_list(folder_old,folder_new,3,list_yes)
    count_global = len(list_yes)


# 主程序
if __name__ == '__main__':
    start_time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
## \033[1m粗体
## \033[34m蓝色
    print('\033[1m\033[34m已启动 | Running | 始めよか')
    print('[INFO]程序开始时间（北京时间）：', start_time.strftime('%Y-%m-%d %H:%M:%S'))

    count_global = count_files(os.path.join(folder_origin,'Confocal'))
    print(f'\033[0m\033[34m[INFO][1/6] Now {count_global} images')
    
    folder_preparation()
    print('[INFO][2/6] Folder-preparation Complete!')
    
    RESHAPE(folder_origin, folder_reshape)
    print(f'[INFO][3/6] Reshaping complete with {count_global} images!')  

    EXPAND(folder_reshape, folder_expand)
    print(f'[INFO][4/6] Expansion complete with {count_global} images!')   

    HIGH_CONTRAST(folder_expand)
    print(f'[INFO][5/6] HIGH_CONTRAST Complete!')   

    PURGE(folder_expand, folder_purge)
    print(f'[INFO][6/6] Purge complete with {count_global} images!')   

    end_time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
    total_time = end_time - start_time

    print('\033[0m\033[1m\033[34m[INFO]程序结束时间（北京时间）：', end_time.strftime('%Y-%m-%d %H:%M:%S'))
    print('[INFO]程序总用时：', total_time)
    print('已结束 | All Complete! | 終了ね\033[0m')