# -*- coding: utf-8 -*-
"""
Created on Mon Oct 17 10:05:10 2022

@author: zannahung
"""

import math
import datetime
import psycopg2
import pandas as pd
from custom_modules.connection import sql_select_

# %% load data

query = '''
Select T1.ID
      ,T1.Product_GUID
      ,T1.Eslite_SN
      ,Left(replace(replace(replace(replace(T1.Short_Description,'<br/>','  '),'<br>','  '),chr(13),'  '),chr(10),'  '),165)  As Short_Description
      ,T1.Retail_Price
      ,T1.Retail_Price_Upd_Note
      ,T1.EC_Price
      ,T1.Sale_Mode
      ,To_Char(T1.Active_Start_Date + interval '8 Hour','YYYY-MM-DD HH24:MI:SS')    As Active_Start_Date
      ,To_Char(T1.Active_End_Date + interval '8 Hour','YYYY-MM-DD HH24:MI:SS')      As Active_End_Date
      ,To_Char(T1.Created_At + interval '8 Hour','YYYY-MM-DD HH24:MI:SS')           As Created_At
      ,(Case When T1.Is_Shipped_Separately = 'Y' Then 'Y'
             When T1.Is_Shipped_Separately = 'N' Then 'N'
        	  Else Null End)                                                         As Is_Shipped_Separately
      ,T2.name                                                                     AS brand_name
  From Products T1 left outer join public.brands t2
    on t1.brand_id = t2.id
 Where (Case When T1.Sale_Mode = 1 Then Coalesce(T1.Virtual_Stock,0) - Coalesce(T1.Share_Reserve_Stock,0) 
			 Else Coalesce(T1.C101_Online_Stock,0)+Coalesce(T1.B2B_Online_Stock,0)+Coalesce(T1.Ingram_Online_Stock,0)+Coalesce(T1.External_Online_Stock,0)-Coalesce(T1.Share_Reserve_Stock,0)
			 End) >= 1
   And T1.Is_Hidden = False
   And T1.Is_Active = True
   And Substring(T1.Eslite_SN,1,2) In ('20','26')
;'''
df = sql_select_('alloydb_prod', query)
df['id'] = df['id'].astype(pd.Int64Dtype())
df['sale_mode'] = df['sale_mode'].astype(pd.Int64Dtype())
df['short_description'] = df['short_description'].str[:200]


# %% export to csv
today = datetime.date.today().strftime('%Y%m%d')
yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y%m%d')
num = 100000
x = math.ceil(len(df)/num)
i = 0
for seq in range(1,x+1): 
    chunk = df.iloc[i:i+num]
    chunk.to_csv('C:/ODS_DATA/output/ODSECS2-PRODUCT-IU-{}-{:0>2}.csv'.format(today, seq), 
                 index=False, 
                 header=False, 
                 sep='\1', # SOH分隔符號
                 encoding='utf-8-sig')
    i = i+num
