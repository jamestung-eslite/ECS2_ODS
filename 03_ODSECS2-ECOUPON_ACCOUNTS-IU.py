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
#yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y%m%d')

# 平常跑昨天
target_date = datetime.date.today() - datetime.timedelta(days=1)

# 回補指定日期
# target_date = datetime.date(2026, 6, 27)

start = datetime.datetime.combine(target_date, datetime.time.min)
end = start + datetime.timedelta(days=1)

# 轉 UTC
start_utc = start - datetime.timedelta(hours=8)
end_utc = end - datetime.timedelta(hours=8)


# 1. 執行邊界查詢，取得 min_id 與 max_id
boundary_sql = f"""
    SELECT MIN(id) AS min_id, MAX(id) AS max_id 
    FROM ecoupon_accounts 
    WHERE updated_at >= '{start_utc}' AND updated_at < '{end_utc}'
"""
boundary_df = sql_select_('alloydb_prod', boundary_sql)

dfs = []

# 檢查是否有查到資料
if not boundary_df.empty and boundary_df['min_id'].iloc[0] is not None:
    min_id = int(boundary_df['min_id'].iloc[0])
    max_id = int(boundary_df['max_id'].iloc[0])

    # 2. 採用固定 ID 區間分頁 (chunk_size 可依記憶體情況調至 20000~50000)
    chunk_size = 10000
    current_id = min_id

    while current_id <= max_id:
        next_id = current_id + chunk_size
        sql = f"""
            SELECT
                ea.id,
                es.ecoupon_id,
                ea.used_at,
                ea.created_at,
                ea.updated_at,
                m.uuid
            FROM ecoupon_accounts ea
            JOIN ecoupon_send_infos es ON ea.ecoupon_send_info_id = es.id
            JOIN members m ON m.id = ea.member_id
            WHERE ea.id >= {current_id} AND ea.id < {next_id}
              AND ea.updated_at >= '{start_utc}' AND ea.updated_at < '{end_utc}'
        """
        
        chunk_df = sql_select_('alloydb_prod', sql)

        # 無資料時繼續下一個區間，不可 break
        if not chunk_df.empty:
            chunk_df['id'] = chunk_df['id'].astype('int64')
            chunk_df['ecoupon_id'] = chunk_df['ecoupon_id'].astype('Int64')
            dfs.append(chunk_df)

        current_id = next_id

# 3. 合併並於 Pandas 端處理時區補償 (+8hr) 與格式化
if dfs:
    df = pd.concat(dfs, ignore_index=True)
    
    # 將 UTC 時間轉回 +8 小時並格式化為字串 (對齊原本 DB 的 to_char 格式)
    time_cols = ['used_at', 'created_at', 'updated_at']
    for col in time_cols:
        df[col] = pd.to_datetime(df[col]) + pd.Timedelta(hours=8)
        df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S').fillna('')
else:
    df = pd.DataFrame(columns=['id', 'ecoupon_id', 'used_at', 'created_at', 'updated_at', 'uuid'])


#%% 切割Dataframe成檔案

num = 100000
x = math.ceil(len(df)/num)
i = 0
for seq in range(1,x+1): 
    chunk = df.iloc[i:i+num]
    chunk.to_csv('C:/ODS_DATA/output/ODSECS2-ECOUPON_ACCOUNTS-IU-{}-{:0>2}.csv'.format(today, seq)
                 , index=False
                 , header=False
                 , sep='\1' #SOH分隔符號
                 , encoding='utf-8-sig')
    i = i+num
