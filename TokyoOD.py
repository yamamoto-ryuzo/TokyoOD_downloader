#2024/08/18 作成開始　とりあえず一覧取得から

#pip install pygeos

import geopandas as gpd
import pandas as pd

###########################################
######## 自作関数ファイルを読み込み #########
###########################################
import TokyoOD_functions

#########################
######## メイン #########
########################
try:
    url = "https://catalog.data.metro.tokyo.lg.jp/csv/export"
    q = "トイレ"
    format = "CSV"

    df = TokyoOD_functions.fetch_data_from_url(url, q, format)
    if df is not None:
        print(df)
    
# エラー処理
except FileNotFoundError:
    print(f"ファイルが見つかりません。")
except Exception as e:
    print(f"エラーが発生しました: {e}")