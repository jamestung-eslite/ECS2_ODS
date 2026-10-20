# -*- coding: utf-8 -*-
"""
Created on Mon Dec 13 17:50:40 2021

@author: evonnekuo
"""

import datetime
import math
import pandas as pd
from custom_modules.connection import sql_select_
today = datetime.date.today().strftime('%Y%m%d')
yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y%m%d')
#%%從PostgreSQL撈取資料

sql = '''(select main_order_id,
                 lidm,
                 cardnumber
                 from payment_histories
                 where cardnumber is not null
                 and to_char(updated_at ,'YYYYMMDD') = to_char(Current_timestamp at time zone 'Asia/Taipei' - Interval '1 Day','YYYYMMDD') 
                 group by main_order_id,lidm,cardnumber)
                 
          union all
          
         (select  main_order_id,
                 lidm,
                 bin_code as cardnumber
            from payment_histories
           where is_tappay='Y'
             and transaction_method_reference='REQUEST'
             and bin_code is not null
             and last4digitpan is not null
             and to_char(updated_at + interval '8 Hour','YYYYMMDD') = to_char(Current_timestamp at time zone 'Asia/Taipei' - Interval '1 Day','YYYYMMDD') 
           group by main_order_id,lidm,bin_code)
      ;'''

df = sql_select_('alloydb_prod', sql)
df['main_order_id'] = df['main_order_id'].astype(pd.Int64Dtype())

#%% 切割Dataframe成檔案

num = 100000
x = math.ceil(len(df)/num)
i = 0
for seq in range(1,x+1): 
    chunk = df.iloc[i:i+num]
    chunk.to_csv('C:/ODS_DATA/output/ODSECS2-CREDIT_CARD-IU-{}-{:0>2}.csv'.format(today, seq)
                 , index=False
                 , header=False
                 , sep='\1' #SOH分隔符號
                 , encoding='utf-8-sig')
    i = i+num
