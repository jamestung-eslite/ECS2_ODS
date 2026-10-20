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
#%%從PostgreSQL撈取資料 原只提供異動的明細資料 調整為整單明細資料

sql = '''
select Distinct 
       T3.id,
       T3.main_order_id,
       T3.sub_order_id,
       to_char(T3.created_at + interval '8 Hour','YYYY-MM-DD HH24:MI:SS') as created_at,
       to_char(T3.updated_at + interval '8 Hour','YYYY-MM-DD HH24:MI:SS') as updated_at,
       T3.eslite_sn,
       SUBSTRING(replace(Replace(Replace(T3.product_name,E'\n',''),E'\r',''),',',''),1,130) as product_name,
       T3.quantity,
       T3.final_price,
       T3.retail_price,
       T3.actually_price,
       (case when T3.discount_amount_price>0 then T3.discount_amount_price
       else T3.cart_discount_amount_price+T3.ecoupon_discount_amount_price end ) as discount_price,
       T3.cargo_company,
       SUBSTRING(replace(Replace(Replace(T3.cargo_number,E'\n',''),E'\r',''),',',''),1,6) as cargo_number,
       Substring(T3.MCH,1,9) As mch_n,
       T3.is_preorder,
       T3.is_gift,
       replace(T3.package_notes,',','') as package_notes,       
       --replace(T3.shipping_notes,',','') as shipping_notes,
       Left(replace(replace(replace(replace(T3.Shipping_Notes,'<br/>','  '),'<br>','  '),chr(13),'  '),chr(10),'  '),100)  As shipping_notes,        
       '' as tax,
       '' as untaxamount,
       T3.eslite_discount_amount_price
  from sub_order_items T3
 inner join sub_orders T2
    on T3.sub_order_id=T2.id
 where T2.status  in (4,5,6)
   and to_char(T2.updated_at + interval '8 Hour','YYYYMMDD') >= to_char(Current_timestamp at time zone 'Asia/Taipei' - Interval '1 Day','YYYYMMDD') 
 Union
Select Distinct 
       T3.ID,
       T3.Main_Order_ID,
       T3.Sub_Order_ID,
       To_Char(T3.Created_At + Interval '8 Hour','YYYY-MM-DD HH24:MI:SS') As Created_At,
       To_Char(T3.Updated_At + Interval '8 Hour','YYYY-MM-DD HH24:MI:SS') As Updated_At,
       T3.Eslite_Sn,
       SUBSTRING(replace(Replace(Replace(T3.product_name,E'\n',''),E'\r',''),',',''),1,130) as product_name,
       T3.Quantity,
       T3.Final_Price,
       T3.Retail_Price,
       T3.Actually_Price,
       (Case When T3.Discount_Amount_Price > 0 Then T3.Discount_Amount_Price
             Else T3.Cart_Discount_Amount_Price+T3.Ecoupon_Discount_Amount_Price End ) As Discount_Price,
       T3.Cargo_Company,
       SUBSTRING(replace(Replace(Replace(T3.cargo_number,E'\n',''),E'\r',''),',',''),1,6) as cargo_number,
       Substring(T3.MCH,1,9) As mch_n,
       T3.Is_Preorder,
       T3.Is_Gift,
       replace(T3.Package_Notes,',','') as Package_Notes,
       --replace(T3.Shipping_Notes,',','') as Shipping_Notes,
       Left(replace(replace(replace(replace(T3.Shipping_Notes,'<br/>','  '),'<br>','  '),chr(13),'  '),chr(10),'  '),100)  As shipping_notes, 
       '' as Tax,
       '' as Untaxamount,
       T3.Eslite_Discount_Amount_Price
  from (Select Distinct R2.Sub_Order_ID
          From return_sub_order_items R2
         Inner Join Return_Sub_Orders R1
            On R2.Return_Sub_Order_ID=R1.ID
         where R1.Status=3
           And To_Char(R1.Updated_At + interval '8 Hour','YYYYMMDD') >= To_Char(Current_timestamp at time zone 'Asia/Taipei' - Interval '1 Day','YYYYMMDD')
       ) Re
 Inner Join Sub_Order_Items T3
    On Re.Sub_Order_ID = T3.Sub_Order_ID
 Inner Join Sub_Orders T2
    on T3.Sub_Order_ID=T2.ID
 Where T2.Status In (4,5,6)
; '''

df = sql_select_('alloydb_prod', sql)
df['id'] = df['id'].astype(pd.Int64Dtype())
df['main_order_id'] = df['main_order_id'].astype(pd.Int64Dtype())
df['sub_order_id'] = df['sub_order_id'].astype(pd.Int64Dtype())
df['quantity'] = df['quantity'].astype(pd.Int64Dtype())
df['retail_price'] = df['retail_price'].astype(pd.Int64Dtype())
df['actually_price'] = df['actually_price'].astype(pd.Int64Dtype())
df['eslite_discount_amount_price'] = df['eslite_discount_amount_price'].astype(pd.Int64Dtype())
df['cargo_number'] = df['cargo_number'].replace(r'\n',  '', regex=True)

#%% 切割Dataframe成檔案

num = 100000
x = math.ceil(len(df)/num)
i = 0
for seq in range(1,x+1): 
    chunk = df.iloc[i:i+num]
    chunk.to_csv('C:/ODS_DATA/output/ODSECS2-SUB_ORDER_ITEMS-IU-{}-{:0>2}.csv'.format(today, seq)
                 , index=False
                 , header=False
                 , sep='\1' #SOH分隔符號
                 , encoding='utf-8-sig')
    i = i+num
