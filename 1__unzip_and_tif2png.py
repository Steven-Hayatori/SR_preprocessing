introduction = str("[INFO]本文件主要完成两个任务：\n\t任务一：将-1downloaded中各文件夹（即拍摄趟次）中的zip文件中有效图片（指一组Confocal和STED）解压并标准化命名至0TIF文件夹下\n\t任务二：将0TIF中16位TIF文件转换成8位png文件")

import os
import shutil
import zipfile
import numpy as np
from PIL import Image

import datetime


# 基本参数
folder_download = r"./-1download"
folder_TIF = r"./0TIF"
folder_origin = r'./1origin'

# 辅助函数
## 获取当前目录下所有文件夹，输出一个list
def get_folders(directory):
    folders = []
    for filename in os.listdir(directory):
        if os.path.isdir(os.path.join(directory, filename)):
            folders.append(filename)
    return folders

## 获取当前目录下所有zip文件全名（a.zip），输出一个list
def get_compressed_files(directory):
    compressed_files = []
    for filename in os.listdir(directory):
        if filename.endswith('.zip'):
            compressed_files.append(filename)
    return compressed_files

## 将一个压缩文件"zip_path"中"targetfile_fullname"文件解压到"extract_dir"并重命名为"newfile_fullname"
    ### r指的是read模式
def extract_specific_file(zip_path, targetfile_fullname, extract_dir, newfile_fullname):
    with zipfile.ZipFile(zip_path, 'r') as target_zip:
        if targetfile_fullname in target_zip.namelist():
            target_zip.extract(targetfile_fullname, extract_dir)
            os.rename(os.path.join(extract_dir, targetfile_fullname), os.path.join(extract_dir, newfile_fullname))

## 创建目录
def create_folder(dir_path):
    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path)
        except OSError as e:
            print(f"创建目录 {dir_path}' 失败：{e}")

## 删除目录和文件
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

# 主函数
def folder_preparation():
    delete_folder(folder_TIF)
    delete_folder(folder_origin)
    create_folder(os.path.join(folder_TIF,'Confocal'))
    create_folder(os.path.join(folder_TIF,'STED'))
    create_folder(os.path.join(folder_origin,'Confocal'))
    create_folder(os.path.join(folder_origin,'STED'))

def unzip(folder_old, folder_new):
    global count_global
    list_folder = get_folders(folder_old)
    for folder_i in list_folder:
        list_zip = get_compressed_files(os.path.join(folder_old,folder_i))
        for zip_i in list_zip:
            shortname = zip_i.split('.')[0]
            # name_Confocal = firstname + '_Confocal.raw.tif'
            name_Confocal = shortname + '_STAR RED.Confocal.ome.tif'
            name_STED = shortname + '_STAR RED.STED.ome.tif'
            name_Confocal_sorted = str(count_global) + '_Confocal' + '.tif'
            name_STED_sorted = str(count_global) + '_STED' + '.tif'
            # 从a压缩文件种解压出b文件，放入c目录，重命名为d
            extract_specific_file(os.path.join(folder_old,folder_i,zip_i), name_Confocal, os.path.join(folder_new,'Confocal'), name_Confocal_sorted)
            extract_specific_file(os.path.join(folder_old,folder_i,zip_i), name_STED, os.path.join(folder_new,'STED'), name_STED_sorted)
            count_global += 1

def TIF2PNG(folder_old, folder_new):
    types = ['Confocal','STED']
    for type in types:
        dir_old = os.path.join(folder_old,type)
        dir_new = os.path.join(folder_new,type)
        for file in os.listdir(dir_old):
            newfullname = str(file.split('.')[0]) + '.png'
            TIF_Image = Image.open(os.path.join(dir_old,file))
            TIF_array = np.array(TIF_Image)
            max_value = np.max(TIF_array)
            min_value = np.min(TIF_array)
            mapped_array = ((TIF_array - min_value) / (max_value - min_value) * 255).astype(np.uint8)
            png_image = Image.fromarray(mapped_array)
            png_image.save(os.path.join(dir_new,newfullname), format='PNG')
          
# 主程序
if __name__ == '__main__':
    start_time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
## \033[1m粗体
## \033[34m蓝色
## \033[0m去除格式
    print('\033[1m\033[34m已启动 | Running | 始めよか')
    print('[INFO]程序开始时间（北京时间）：', start_time.strftime('%Y-%m-%d %H:%M:%S'))

    print(introduction)
    count_global = 0

    folder_preparation()
    print('\033[0m\033[34m[INFO][1/3] Folder-preparation Complete!')
    unzip(folder_download,folder_TIF)
    print('[INFO][2/3] Unzipping Complete!')
    TIF2PNG(folder_TIF,folder_origin)
    print('[INFO][3/3] TIF2PNG Complete!')

    end_time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8)))
    total_time = end_time - start_time
    print(f'一共{count_global+1}组图片，序列从0至{count_global}')

    print('\033[0m\033[1m\033[34m[INFO]程序结束时间（北京时间）：', end_time.strftime('%Y-%m-%d %H:%M:%S'))
    print('[INFO]程序总用时：', total_time)
    print('已结束 | All Complete! | 終了ね\033[0m')
