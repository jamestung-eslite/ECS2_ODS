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
       T1.id,
       T1.cart_id,
       m.uuid,
       to_char(T1.created_at + interval '8 Hour','YYYY-MM-DD HH24:MI:SS') as created_at,
       to_char(T1.updated_at + interval '8 Hour','YYYY-MM-DD HH24:MI:SS') as updated_at,
       T1.order_number,
       T1.profit_center,
       T1.payment_type,
       T1.payment_status,
       T1.shopee_order_id,
       T1.shipping_type,
       T1.recipient_store_id,
       replace(T1.recipient_store_name,',',''),
       T1.recipient_store_type,
       T1.recipient_zip,
       replace(T1.recipient_country,',','') as recipient_country,
       (case when T1.shipping_type in ('3','5','9') then ''
       else replace(T1.recipient_city,',','') end) as recipient_city,
       (case when T1.shipping_type in ('3','5','9') then ''
       else replace(T1.recipient_district,',','') end) as recipient_district,
       (case when T1.shipping_type in ('3','5','9') then replace(T1.recipient_address,',','')
       else '' end) as recipient_address,  --僅超取給地址
       Coalesce(T1.Invoice_Type,0) As invoice_type,
       T1.taxid,
       replace(T1.utm_url,',','') As Utm_Url,
       T1.Order_Source,
       T1.bank_id,
       T1.installment_period,
       I1.invoice_number,
       to_char(I1.updated_at + interval '8 Hour','YYYY-MM-DD HH24:MI:SS') as invoice_date,
       T1.eslite_discount_amount,
       T1.amount
  from main_orders T1
 Inner Join Sub_Orders T2
    On T1.ID = T2.Main_Order_ID
 inner join members m
    on T1.member_id=m.id
  left join (Select II1.main_order_id
                   ,Max(II1.created_at)     As created_at
                   ,Max(II1.updated_at)     As updated_at
                   ,Max(II1.invoice_number) As invoice_number
               From invoices II1
          	  where II1.status = 1
              Group By II1.main_order_id) I1
    on T1.ID = I1.main_order_id
 --And I1.Status = 1
 where to_char(T2.updated_at + interval '8 Hour','YYYYMMDD') >= to_char(Current_timestamp at time zone 'Asia/Taipei' - Interval '1 Day','YYYYMMDD')
   And Exists (Select TT2.Main_Order_ID
                     ,Max(TT2.Status) 
                 From Sub_Orders TT2
                Where T1.ID = TT2.Main_Order_ID 
                  And TT2.Status Not In (7,8)
                Group By TT2.Main_Order_ID 
               Having Max(TT2.Status) In (4,5,6))
Union 
Select Distinct 
       T1.ID,
       T1.Cart_ID,
       m.UUID,
       to_char(T1.created_at + interval '8 Hour','YYYY-MM-DD HH24:MI:SS') as Created_At,
       to_char(T1.updated_at + interval '8 Hour','YYYY-MM-DD HH24:MI:SS') as Updated_At,
       T1.Order_Number,
       T1.Profit_Center,
       T1.Payment_Type,
       T1.Payment_Status,
       T1.Shopee_Order_ID,
       T1.Shipping_Type,
       T1.Recipient_Store_ID,
       replace(T1.Recipient_Store_Name,',','') As Recipient_Store_Name,
       T1.Recipient_Store_Type,
       T1.Recipient_Zip,
       replace(T1.recipient_country,',','') as Recipient_Country,       
       (Case When T1.Shipping_Type In ('3','5','9') Then ''
             Else Replace(T1.Recipient_City,',','') end) As Recipient_City,
       (Case When T1.Shipping_Type In ('3','5','9') Then ''
             Else Replace(T1.Recipient_District,',','') End) As Recipient_District,
       (Case When T1.Shipping_Type In ('3','5','9') Then Replace(T1.Recipient_Address,',','')
             Else '' End) As recipient_address,  --僅超取給地址
       Coalesce(T1.Invoice_Type,0) As Invoice_Type,
       T1.TaxID,
       replace(T1.utm_url,',','') As Utm_Url,
       T1.Order_Source,
       T1.Bank_ID,
       T1.Installment_Period,
       I1.Invoice_Number,
       To_Char(I1.Updated_At + Interval '8 Hour','YYYY-MM-DD HH24:MI:SS') As Invoice_Date,
       T1.Eslite_Discount_Amount,
       T1.Amount
  From (Select Distinct R1.Main_Order_ID 
          From return_sub_order_items R2
         Inner Join Return_Sub_Orders R1
            On R2.Return_Sub_Order_ID=R1.ID
         where R1.Status=3
           And To_Char(R1.Updated_At + interval '8 Hour','YYYYMMDD') >= To_Char(Current_timestamp at time zone 'Asia/Taipei' - Interval '1 Day','YYYYMMDD')
       ) Re
 Inner Join main_orders T1
    On Re.Main_Order_ID = T1.ID
 Inner Join Sub_Orders T2
    On T1.ID = T2.Main_Order_ID
 Inner Join Members m
    on T1.Member_ID=m.ID
  Left Join (Select II1.main_order_id
                   ,Max(II1.created_at)     As created_at
                   ,Max(II1.updated_at)     As updated_at
                   ,Max(II1.invoice_number) As invoice_number
               From invoices II1
              where II1.status = 1               
              Group By II1.main_order_id) I1
    On T1.ID=I1.Main_Order_ID
 --And I1.Status = 1 
 where Exists (Select TT2.Main_Order_ID
                     ,Max(TT2.Status) 
                 From Sub_Orders TT2
                Where T1.ID = TT2.Main_Order_ID 
                  And TT2.Status Not In (7,8)
                Group By TT2.Main_Order_ID 
               Having Max(TT2.Status) In (4,5,6))
;'''

df = sql_select_('alloydb_prod', sql)
df['id'] = df['id'].astype(pd.Int64Dtype())
df['cart_id'] = df['cart_id'].astype(pd.Int64Dtype())
df['invoice_type'] = df['invoice_type'].astype(pd.Int64Dtype())
df['installment_period'] = df['installment_period'].astype(pd.Int64Dtype())
df["utm_url"] = df["utm_url"].str.replace(r"&utm_term(?:%\d{2}|%\d{4})\D=undefined", "", regex=True)

#%% 切割Dataframe成檔案

num = 100000
x = math.ceil(len(df)/num)
i = 0
for seq in range(1,x+1): 
    chunk = df.iloc[i:i+num]
    chunk.to_csv('C:/ODS_DATA/output/ODSECS2-MAIN_ORDERS-IU-{}-{:0>2}.csv'.format(today, seq)
                 , index=False
                 , header=False
                 , sep='\1' #SOH分隔符號
                 , encoding='utf-8-sig')
    i = i+num
