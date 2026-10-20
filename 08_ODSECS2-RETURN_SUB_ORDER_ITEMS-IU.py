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

sql = '''select R2.id,
                R2.sub_order_id,
                R1.main_order_id,
                R2.sub_order_item_id,
                to_char(R2.created_at + interval '8 Hour','YYYY-MM-DD HH24:MI:SS'),
                to_char(R2.updated_at + interval '8 Hour','YYYY-MM-DD HH24:MI:SS'),
                R1.status,
                R1.return_type,
                R2.price,
                R2.qty,
                (case when R2.esp_invoice_number_revoked_date is null then to_char(R1.finished_at + interval '8 Hour','YYYY-MM-DD')
                      else to_char(R2.esp_invoice_number_revoked_date + interval '8 Hour','YYYY-MM-DD') end ) as esp_invoice_number_revoked_date,
                '' as tax,
                '' as untaxamount,
                R2.eslite_point 
           from return_sub_order_items R2
          inner join return_sub_orders R1
             on R2.return_sub_order_id=R1.id
          where R1.status=3
            and to_char(R1.updated_at + interval '8 Hour','YYYYMMDD') >= to_char(Current_timestamp at time zone 'Asia/Taipei' - Interval '1 Day','YYYYMMDD') 
      '''

df = sql_select_('alloydb_prod', sql)
df['id'] = df['id'].astype(pd.Int64Dtype())
df['sub_order_id'] = df['sub_order_id'].astype(pd.Int64Dtype())
df['main_order_id'] = df['main_order_id'].astype(pd.Int64Dtype())
df['sub_order_item_id'] = df['sub_order_item_id'].astype(pd.Int64Dtype())
df['status'] = df['status'].astype(pd.Int64Dtype())
df['return_type'] = df['return_type'].astype(pd.Int64Dtype())
df['price'] = df['price'].astype(pd.Int64Dtype())
df['qty'] = df['qty'].astype(pd.Int64Dtype())
df['eslite_point'] = df['eslite_point'].astype(pd.Int64Dtype())

#%% 切割Dataframe成檔案

num = 100000
x = math.ceil(len(df)/num)
i = 0
for seq in range(1,x+1): 
    chunk = df.iloc[i:i+num]
    chunk.to_csv('C:/ODS_DATA/output/ODSECS2-RETURN_SUB_ORDER_ITEMS-IU-{}-{:0>2}.csv'.format(today, seq)
                 , index=False
                 , header=False
                 , sep='\1' #SOH分隔符號
                 , encoding='utf-8-sig')
    i = i+num
