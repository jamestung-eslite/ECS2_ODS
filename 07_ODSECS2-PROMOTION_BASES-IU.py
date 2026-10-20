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

sql = '''select pb.id,
                SUBSTRING(replace(pb.name,',',''),1,100),
                SUBSTRING(replace(pb.description,',',''),1,100),
                SUBSTRING(replace(pb.coupon_name,',',''),1,100),
                to_char(pb.started_at + interval '8Hour','YYYY-MM-DD HH24:MI:SS'),
                (case when to_char(pb.ended_at,'YYYY-MM-DD HH24:MI:SS') ='9999-12-31 23:59:59' 
                 then to_char(pb.ended_at,'YYYY-MM-DD HH24:MI:SS') 
                 else to_char(pb.ended_at + interval '8Hour','YYYY-MM-DD HH24:MI:SS') end ) as ended_at ,
                pb.hall_type,
                pb.coupon_max_count,
                pb.discount_situation,
                pb.discount_type,
                pb.serial_number,
                pb.type,
                to_char(pb.created_at + interval '8Hour','YYYY-MM-DD'),
                to_char(pb.updated_at + interval '8Hour','YYYY-MM-DD'),
                min(es.send_type) as send_type,
                sum(es.send_qty) as send_qty,
                dynamic,
                dynamic_start_days,
                dynamic_end_days
           from promotion_bases pb
           left join ecoupon_send_infos es
             on pb.id=es.ecoupon_id
          where (to_char(pb.updated_at + interval '8 Hour','YYYYMMDD')= to_char(Current_timestamp at time zone 'Asia/Taipei' - Interval '1 Day','YYYYMMDD') 
             or to_char(es.updated_at + interval '8 Hour','YYYYMMDD')= to_char(Current_timestamp at time zone 'Asia/Taipei' - Interval '1 Day','YYYYMMDD')  )
          group by pb.id
      '''

df = sql_select_('alloydb_prod', sql)
df['id'] = df['id'].astype(pd.Int64Dtype())
df['hall_type'] = df['hall_type'].astype(pd.Int64Dtype())
df['coupon_max_count'] = df['coupon_max_count'].astype(pd.Int64Dtype())
df['discount_situation'] = df['discount_situation'].astype(pd.Int64Dtype())
df['discount_type'] = df['discount_type'].astype(pd.Int64Dtype())
df['send_type'] = df['send_type'].astype(pd.Int64Dtype())
df['send_qty'] = df['send_qty'].astype(pd.Int64Dtype())

#%% 切割Dataframe成檔案

num = 100000
x = math.ceil(len(df)/num)
i = 0
for seq in range(1,x+1): 
    chunk = df.iloc[i:i+num]
    chunk.to_csv('C:/ODS_DATA/output/ODSECS2-PROMOTION_BASES-IU-{}-{:0>2}.csv'.format(today, seq)
                 , index=False
                 , header=False
                 , sep='\1' #SOH分隔符號
                 , encoding='utf-8-sig')
    i = i+num
