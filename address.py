##########################
######## 使いかた #########
##########################
###　入力
#市区町村名 住居表示－街区マスター位置参照拡張 データセット
#"gaiku_url_list.txt　にURLを入力
#市区町村名 住居表示－住居マスター位置参照拡張 データセット
#"jyuukyo_url_list.txt"にURLを入力
###　出力
# 二つのデータセットを統合し、住居データとして出力
#'result/merged_jyuukyo.csv' ファイルが出力されます
#workフォルダには作業の状況が残ります
#ただし、work/extracted_filesフォルダ内は最後に作用した状況のみです

##################################################################
######### モジュール(module)やパッケージ(package)の読み込み #########
##################################################################
#Webページやデータを取得
import requests
#ZIPの圧縮・解凍
import zipfile
#OS依存機能を利用
import os
#データ分析作業を支援するためのモジュール
import pandas as pd
import shutil
import geopandas as gpd
from shapely.geometry import Point

###########################################
######## 自作関数ファイルを読み込み #########
###########################################
import GIF_functions

#########################
######## メイン #########
########################
try:
    ### work　フォルダのクリーニング
    work_folder_path = 'work'
    if os.path.exists(work_folder_path):
        shutil.rmtree(work_folder_path)
    os.makedirs(work_folder_path)
    print(f"workフォルダのクリーニングが完了しました。")

    ### 住居表示ファイルの取得及び結合
    # address_download("住居表示ファイル名一覧ファイル名を指定",'結合住居表示ファイル名')
    #市区町村名 住居表示－街区マスター位置参照拡張 データセット
    GIF_functions.address_download("input_list/gaiku_url_list.txt",'work/combined_gaiku.csv')
    print(f"市区町村名 住居表示－街区マスターが作成されました。")
    #市区町村名 住居表示－住居マスター位置参照拡張 データセット
    GIF_functions.address_download("input_list/jyuukyo_url_list.txt",'work/combined_jyuukyo.csv')
    print(f"市区町村名 住居表示－住居マスターが作成されました。")

    ###　住居マスターに街区マスターを結合する
    # 住居マスターCSVファイルを全て文字列として読み込む
    df1 = pd.read_csv('work/combined_jyuukyo.csv', dtype=str)
    # 街区マスターCSVファイルを全て文字列として読み込む
    df2 = pd.read_csv('work/combined_gaiku.csv', dtype=str)
    # 初期化
    merged_df = pd.DataFrame()
    #df2 に重複がある場合削除
    df2_unique = df2.drop_duplicates(subset='街区ユニークid')
    # 属性をキーにして結合
    # 結合方式はleftのすべての行が保持
    # 同じ属性が重複する場合は街区データ側に接尾辞を追加
    merged_df = pd.merge(df1, df2_unique, on='街区ユニークid', how='left', suffixes=('', '_街区'))
    # '_街区'のついた属性を削除
    filtered_columns = merged_df.filter(regex='_街区$', axis=1).columns
    merged_df.drop(columns=filtered_columns, inplace=True)
    # 結合したい文字列の属性を選択し、新しい文字列の属性 ['所在地_連結表記'] を作成する
    merged_df['所在地_連結表記'] = merged_df['位置参照情報_都道府県名']+merged_df['位置参照情報_市区町村名']+merged_df['位置参照情報_大字・町丁目名'] + merged_df['街区id'].str.lstrip("0") + "-" + merged_df['住居id'].str.lstrip("0")
    csv_file_path = 'result/jyuukyo.csv'
    # 結合結果を新しいCSVファイルとして保存
    merged_df.to_csv(csv_file_path, index=False)
    print(f"居住データベースが作成されました。")

        # GPKGに変換して保存
    # "latitude" と "longitude" 列からPointオブジェクトを作成する
    geometry = [Point(xy) for xy in zip(merged_df['代表点_経度'], merged_df['代表点_緯度'])]
    # GeoDataFrameを作成し、ポイントデータを追加する
    gdf = gpd.GeoDataFrame(merged_df, geometry=geometry, crs="EPSG:6668")  # 初期の座標系を指定
    # GeoPackage形式で保存
    gdf.to_file("result/jyuukyo.gpkg", driver="GPKG")
    print(f"GPKGが作成されました。")

    
# エラー処理
except FileNotFoundError:
    print(f"ファイルが見つかりません。")
except Exception as e:
    print(f"エラーが発生しました: {e}")