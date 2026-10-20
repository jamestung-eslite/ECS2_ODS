# -*- coding: utf-8 -*-
"""
Created on Mon Dec 13 17:50:40 2021

@author: evonnekuo
"""


import math
import datetime
import pandas as pd
from custom_modules.connection import sql_select_

today = datetime.date.today().strftime('%Y%m%d')
yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y%m%d')
#%%從PostgreSQL撈取資料

sql = '''select max(pn.id),
                m.uuid,
                to_char(pn.created_at + interval '8 Hour','YYYY-MM-DD HH24:MI:SS'),
                to_char(max(pn.updated_at) + interval '8 Hour','YYYY-MM-DD HH24:MI:SS'),
                p.eslite_sn
           from product_notifications pn
           join members m
             on pn.member_id=m.id
           join products p
             on pn.product_id=p.id
          where to_char(pn.updated_at + interval '8 Hour','YYYYMMDD') = to_char(Current_timestamp at time zone 'Asia/Taipei' - Interval '1 Day','YYYYMMDD') 
            and p.eslite_sn is not null
          group by m.uuid,to_char(pn.created_at + interval '8 Hour','YYYY-MM-DD HH24:MI:SS'),p.eslite_sn
      '''
df = sql_select_('alloydb_prod', sql)
df['max'] = df['max'].astype(pd.Int64Dtype())

#%% 切割Dataframe成檔案

num = 100000
x = math.ceil(len(df)/num)
i = 0
for seq in range(1,x+1): 
    chunk = df.iloc[i:i+num]
    chunk.to_csv('C:/ODS_DATA/output/ODSECS2-PRODUCT_NOTIFICATIONS-IU-{}-{:0>2}.csv'.format(today, seq)
                 , index=False
                 , header=False
                 , sep='\1' #SOH分隔符號
                 , encoding='utf-8-sig')
    i = i+num
