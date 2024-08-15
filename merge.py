#2024/03/03　データが多いととても遅く、メモリーエラーも発生
#QGISのベクタ＞ベクタ管理ツール＞マージを利用

#pip install pygeos

import geopandas as gpd
import pandas as pd

#########################
######## メイン #########
########################
try:
    # 入力ファイルパス
    file1 = r"result\digital_national_land_information.gpkg"
    file2 = r"result\jyuukyo.gpkg"
    # GeoDataFrame としてファイルを読み込む
    gdf1 = gpd.read_file(file1)
    gdf2 = gpd.read_file(file2)
    # EPSG:6668 に統一
    print(f"CRSを確認します：{gdf1.crs}/FILE:{file1}")
    if gdf1.crs != {'init': 'EPSG:6668'}:
        gdf1 = gdf1.to_crs(epsg=6668)
        print(f"CRSをEPSG:6668に統一しました。")
    print(f"CRSを確認します：{gdf2.crs}/FILE:{file2}")
    if gdf2.crs != {'init': 'EPSG:6668'}:
        gdf2 = gdf2.to_crs(epsg=6668)
        print(f"CRSをEPSG:6668に統一しました。")
    # データをマージする
    merged_gdf = gpd.GeoDataFrame(pd.concat([gdf1, gdf2], ignore_index=True))
    # 出力ファイルパス
    output_file = r"result\OpendataBridge.gpkg"
    # マージしたデータを GeoPackage ファイルに保存する
    merged_gdf.to_file(output_file, driver="GPKG")

    
# エラー処理
except FileNotFoundError:
    print(f"ファイルが見つかりません。")
except Exception as e:
    print(f"エラーが発生しました: {e}")