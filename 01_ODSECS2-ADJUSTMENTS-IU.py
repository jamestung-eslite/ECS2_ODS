# -*- coding: utf-8 -*-
"""
Created on Mon Dec 13 17:50:40 2021

@author: evonnekuo
"""

import datetime
import pandas as pd
import math
from custom_modules.connection import sql_select_

today = datetime.date.today().strftime('%Y%m%d')
yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y%m%d')
#%%從PostgreSQL撈取資料

sql = '''select Distinct 
                a.id,
                a.main_order_id,
                a.promotion_id,
                a.ecoupon_id,
                a.ecoupon_account_id,
                replace(a.label,',',''),
                to_char(a.created_at + interval '8 Hour','YYYY-MM-DD HH24:MI:SS'),
                to_char(a.updated_at + interval '8 Hour','YYYY-MM-DD HH24:MI:SS'),
                --c.order_number,
                substr(b.order_number,1,13),
                a.amount*-1
           from adjustments a
          Inner Join Sub_Orders b
             On a.Main_Order_ID = b.Main_Order_ID
          --Inner join main_orders c
          --   on c.id=b.main_order_id     
          where a.main_order_id is not null 
            and to_char(b.updated_at + interval '8 Hour','YYYYMMDD') = to_char(Current_timestamp at time zone 'Asia/Taipei' - Interval '1 Day','YYYYMMDD')
            And Exists (Select T2.Main_Order_ID
                              ,Max(T2.Status) 
                          From Sub_Orders T2
                         Where a.Main_Order_ID = T2.Main_Order_ID 
                           and T2.Status not In ( 7,8 )
                         Group By T2.Main_Order_ID 
                        Having Max(T2.Status) In (4,5,6))
                   
      '''

df = sql_select_('alloydb_prod', sql)
df['id'] = df['id'].astype(pd.Int64Dtype())
df['main_order_id'] = df['main_order_id'].astype(pd.Int64Dtype())
df['promotion_id'] = df['promotion_id'].astype(pd.Int64Dtype())
df['ecoupon_id'] = df['ecoupon_id'].astype(pd.Int64Dtype())
df['ecoupon_account_id'] = df['ecoupon_account_id'].astype(pd.Int64Dtype())

#%% 切割Dataframe成檔案

num = 100000
x = math.ceil(len(df)/num)
i = 0
for seq in range(1,x+1): 
    chunk = df.iloc[i:i+num]
    chunk.to_csv('C:/ODS_DATA/output/ODSECS2-ADJUSTMENTS-IU-{}-{:0>2}.csv'.format(today, seq)
                 , index=False
                 , header=False
                 , sep='\1' #SOH分隔符號
                 , encoding='utf-8-sig')
    i = i+num
