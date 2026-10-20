# -*- coding: utf-8 -*-
"""
Created on Mon Dec 13 17:50:40 2021

@author: evonnekuo
"""

import os
import hashlib
import pandas as pd
import datetime

yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y%m%d')
today = datetime.date.today().strftime('%Y%m%d')
path1 = 'C:/ODS_DATA/output/'
check_file_name = '{}ODSECS2_CHECKFILE_{}.csv'.format(path1, today)
#md5 = hashlib.md5()

data = {}

files = os.listdir(path1) #得到資料夾下的所有檔名稱
for file in files: #遍歷資料夾
    #取得檔名
    filename = os.path.basename(file) 
    data[filename]= {}
    file_path = (path1 + file)
    #開啟檔案
    with open(file_path, "rb") as f:
        #取檔案長度
        lines = len(f.readlines())
        data[filename]['length'] = lines
        #將參考點設置在文件的開頭
        f.seek(0)
        #計算檔案的MD5雜湊值
        buf = f.read()
        md5 = hashlib.md5()
        md5.update(buf)
        hash = md5.hexdigest()
        data[filename]['hash'] = hash
    
    print(filename , data[filename])

combine = pd.DataFrame(data, columns=data.keys()).T
combine = combine[['length','hash']]
print(combine)
combine.to_csv(check_file_name ,header=False ,encoding = 'utf-8-sig')

