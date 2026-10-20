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

sql = '''
select Distinct 
       T2.id,
       T2.main_order_id,
       to_char(T2.created_at + interval '8 Hour','YYYY-MM-DD HH24:MI:SS'),
       to_char(T2.updated_at + interval '8 Hour','YYYY-MM-DD HH24:MI:SS'),
       T2.order_number,
       T2.status,
       T2.is_b2b_order,
       (case when I1.invoice_number is null then T2.esp_invoice_number
       else I1.invoice_number end )as esp_invoice_number,
       (case when I1.invoice_number is null then to_char(T2.esp_invoice_number_created_date + interval '8 Hour','YYYY-MM-DD')
       else to_char(I1.created_at + interval '8 Hour','YYYY-MM-DD') end) as esp_invoice_number_created_date,
       T2.Paid_Card_Level,  --T2.sp19_card_level 20220704修改
       T2.Paid_Promotion_Card_Level,  --T2.sp19_promotion_card_level  20220704修改
       to_char(T2.paid_at + interval '8 Hour','YYYY-MM-DD HH24:MI:SS'),
       to_char(T2.packed_at + interval '8 Hour','YYYY-MM-DD HH24:MI:SS'),
       to_char(T2.shipped_at + interval '8 Hour','YYYY-MM-DD HH24:MI:SS'),
       to_char(T2.arrived_at + interval '8 Hour','YYYY-MM-DD HH24:MI:SS'),
       to_char(T2.finished_at + interval '8 Hour','YYYY-MM-DD HH24:MI:SS'),
       to_char(T2.lms_synced_at + interval '8 Hour','YYYY-MM-DD HH24:MI:SS'),
       to_char(T2.cancelled_lms_synced_at + interval '8 Hour','YYYY-MM-DD HH24:MI:SS')
  from sub_orders T2
 inner join main_orders T1
    on T1.id=T2.main_order_id
  left join (Select II1.main_order_id
                   ,Max(II1.created_at)     As created_at
                   ,Max(II1.updated_at)     As updated_at
                   ,Max(II1.invoice_number) As invoice_number
               From invoices II1
              Group By II1.main_order_id) I1
    on T2.main_order_id=I1.main_order_id
 --and I1.Status = 1
 where T2.status  in (4,5,6)
   and to_char(T2.updated_at + interval '8 Hour','YYYYMMDD') >= to_char(Current_timestamp at time zone 'Asia/Taipei' - Interval '1 Day','YYYYMMDD')
 Union
Select Distinct 
       T2.ID,
       T2.Main_Order_ID,
       To_Char(T2.Created_At + Interval '8 Hour','YYYY-MM-DD HH24:MI:SS') As Created_At,
       To_Char(T2.Updated_At + Interval '8 Hour','YYYY-MM-DD HH24:MI:SS') As Updated_At,
       T2.Order_Number,
       T2.Status,
       T2.Is_B2B_Order,
       (case when I1.Invoice_Number Is Null Then T2.ESP_Invoice_Number
             Else I1.Invoice_Number End ) As ESP_Invoice_Number,
       (Case When I1.Invoice_Number Is Null Then To_Char(T2.ESP_Invoice_Number_Created_Date + Interval '8 Hour','YYYY-MM-DD')
             Else To_Char(I1.Created_At + Interval '8 Hour','YYYY-MM-DD') End) As ESP_Invoice_Number_Created_Date,
       T2.Paid_Card_Level,  --T2.sp19_card_level 20220704修改
       T2.Paid_Promotion_Card_Level,  --T2.sp19_promotion_card_level  20220704修改
       To_Char(T2.Paid_At + Interval '8 Hour','YYYY-MM-DD HH24:MI:SS'),
       To_Char(T2.Packed_At + Interval '8 Hour','YYYY-MM-DD HH24:MI:SS'),
       To_Char(T2.Shipped_At + Interval '8 Hour','YYYY-MM-DD HH24:MI:SS'),
       To_Char(T2.Arrived_At + Interval '8 Hour','YYYY-MM-DD HH24:MI:SS'),
       To_Char(T2.Finished_At + Interval '8 Hour','YYYY-MM-DD HH24:MI:SS'),
       To_Char(T2.Lms_Synced_At + Interval '8 Hour','YYYY-MM-DD HH24:MI:SS'),
       To_Char(T2.Cancelled_Lms_Synced_At + Interval '8 Hour','YYYY-MM-DD HH24:MI:SS')
  From (Select Distinct R1.Sub_Order_ID 
          From return_sub_order_items R2
         Inner Join Return_Sub_Orders R1
            On R2.Return_Sub_Order_ID=R1.ID
         where R1.Status=3
           And To_Char(R1.Updated_At + interval '8 Hour','YYYYMMDD') >= To_Char(Current_timestamp at time zone 'Asia/Taipei' - Interval '1 Day','YYYYMMDD')
       ) Re
 Inner Join sub_orders T2
    On Re.Sub_Order_ID = T2.ID
 inner join main_orders T1
    on T1.id=T2.main_order_id
  left join (Select II1.main_order_id
                   ,Max(II1.created_at)     As created_at
                   ,Max(II1.updated_at)     As updated_at
                   ,Max(II1.invoice_number) As invoice_number
               From invoices II1
              Group By II1.main_order_id) I1
    on T2.main_order_id=I1.main_order_id
 --and I1.Status = 1
 where T2.status  in (4,5,6)
;
'''

df = sql_select_('alloydb_prod', sql)
df['id'] = df['id'].astype(pd.Int64Dtype())
df['main_order_id'] = df['main_order_id'].astype(pd.Int64Dtype())
df['status'] = df['status'].astype(pd.Int64Dtype())


#%% 切割Dataframe成檔案

num = 100000
x = math.ceil(len(df)/num)
i = 0
for seq in range(1,x+1): 
    chunk = df.iloc[i:i+num]
    chunk.to_csv('C:/ODS_DATA/output/ODSECS2-SUB_ORDERS-IU-{}-{:0>2}.csv'.format(today, seq)
                 , index=False
                 , header=False
                 , sep='\1' #SOH分隔符號
                 , encoding='utf-8-sig')
    i = i+num
