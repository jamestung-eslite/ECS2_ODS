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

# %% 從 PostgreSQL / AlloyDB 分批撈取資料

batch_size = 200
last_id = 0
dfs = []

date_filter_sql = """
   and a.created_at >= (
       date_trunc('day', current_timestamp at time zone 'Asia/Taipei')
       - interval '1 day'
       - interval '8 hour'
   )
   and a.created_at < (
       date_trunc('day', current_timestamp at time zone 'Asia/Taipei')
       - interval '8 hour'
   )
"""

max_id_sql = f"""
    select coalesce(max(a.id), 0) as max_id
      from audits a
     where a.auditable_type = 'Member'
       and a.comment = 'login source'
       and a.action = 'login_source_Web'
       {date_filter_sql}
"""

max_id_df = sql_select_('alloydb_prod', max_id_sql)
max_id = int(max_id_df.loc[0, 'max_id'])

while last_id < max_id:
    sql = f"""
        select a.id,
               m.uuid,
               to_char(a.created_at + interval '8 Hour', 'YYYY-MM-DD HH24:MI:SS') as created_at
          from audits a
          join members m
            on a.auditable_id = m.id
         where a.auditable_type = 'Member'
           and a.comment = 'login source'
           and a.action = 'login_source_Web'
           {date_filter_sql}
           and a.id > {last_id}
           and a.id <= {max_id}
         order by a.id
         limit {batch_size}
    """

    chunk_df = sql_select_('alloydb_prod', sql)

    if chunk_df.empty:
        break

    chunk_df['id'] = chunk_df['id'].astype(pd.Int64Dtype())
    dfs.append(chunk_df)

    last_id = int(chunk_df['id'].max())

if dfs:
    df = pd.concat(dfs, ignore_index=True)
else:
    df = pd.DataFrame(columns=['id', 'uuid', 'created_at'])

#%% 切割Dataframe成檔案

num = 100000
x = math.ceil(len(df)/num)
i = 0
for seq in range(1,x+1): 
    chunk = df.iloc[i:i+num]
    chunk.to_csv('C:/ODS_DATA/output/ODSECS2-LOGIN-IU-{}-{:0>2}.csv'.format(today, seq)
                 , index=False
                 , header=False
                 , sep='\1' #SOH分隔符號
                 , encoding='utf-8-sig')
    i = i+num
    