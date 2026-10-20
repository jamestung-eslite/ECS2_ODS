# -*- coding: utf-8 -*-
"""
Created on Tue Mar 28 12:01:54 2023

@author: kettle_user
"""
import os
import shutil
import datetime

today = datetime.date.today().strftime('%Y%m%d')
year = datetime.date.today().strftime('%Y')
month = datetime.date.today().strftime('%m')
day = datetime.date.today().strftime('%d')
folder = 'ods_data'

#%% 壓縮檔案

path1 = 'C:/ODS_DATA/output/'
#path2 = 'C:/ODS_DATA/upload/'
path2 = 'E:/EAI/TW/ECS2/'
path3 = 'C:/ODS_DATA/backup/'
path4 = 'C:/ODS_DATA/EC2GCS/'


file_names_path1 = os.listdir(path1)

#copy path1 data to path2
for file_name in file_names_path1:
    shutil.copy(os.path.join(path1, file_name), path2)
    shutil.copy(os.path.join(path1, file_name), path4)
#zip path1 data to path3
output_filename = path3 + str(today)
shutil.make_archive(output_filename, 'zip', path1)

#remove path1 data
for file_name in file_names_path1:
    os.remove(path1+file_name)

