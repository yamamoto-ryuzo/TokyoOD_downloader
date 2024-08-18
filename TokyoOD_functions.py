##################################################################
######### モジュール(module)やパッケージ(package)の読み込み #########
##################################################################
#Webページやデータを取得
import csv
import requests
#ZIPの圧縮・解凍
import zipfile
#OS依存機能を利用
import os
#データ分析作業を支援するためのモジュール
import pandas as pd
import shutil
#GISデータの処理
#pip install geopandas
import geopandas as gpd
import json
import fiona

import io
from charset_normalizer import detect

###########################
######### 関数定義 #########
###########################
# ---------------------------------------------TokyoODの関数----------------------------------------------

#import requests
#import pandas as pd
#import io
#from charset_normalizer import detect
def fetch_data_from_url(url, q, format):
    """
    指定されたURLに対してPOSTリクエストを送り、CSVデータを取得してDataFrameとして返す関数。

    Parameters:
    url (str): データを取得するためのURL。
    q (str): 検索クエリ。
    format (str): データのフォーマット（例: 'CSV'）。

    Returns:
    pd.DataFrame: 取得したデータを含むDataFrame。取得に失敗した場合はNoneを返す。
    """
    # POSTリクエスト用のデータを構築
    post_data = {
        "q": q,
        "search_url_params": f"res_format={format}"
    }

    # POSTリクエストを送信してファイルをダウンロード
    response = requests.post(url, data=post_data)

    # ステータスコードをチェック（200は成功を意味する）
    if response.status_code == 200:
        # レスポンスの内容を表示
        print(response.text)
        
        # エンコーディングの種類を確認
        detected_encoding = detect(response.content)
        
        # 自動判定では中国語と間違われる可能性があるので、明示的に指定
        response.encoding = "utf-8"
        
        # データをDataFrameとして読み込む
        df = pd.read_csv(io.BytesIO(response.content), encoding=response.encoding)
        return df
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        return None
# 使用例
#url = "https://catalog.data.metro.tokyo.lg.jp/csv/export"
#q = "トイレ"
#format = "CSV"
#
#df = fetch_data_from_url(url, q, format)
#if df is not None:
#    print(df)

# ----------------------------------------------GIF時代の関数----------------------------------------------
###フォルダのクリーニング
#work_folder_path = 'work'
#clean_work_folder(work_folder_path)
def clean_work_folder(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    os.makedirs(folder_path)
    print(f"{folder_path}フォルダのクリーニングが完了しました。")

###ファイルの中にある??を01－47の連番にして新しいファイルを作成する
#input_filename = 'input.txt'  # 元のファイル名
#output_filename = 'output.txt'  # 出力先のファイル名
#process_file(input_filename, output_filename)
def process_file(input_file, output_file):
    # ファイルからデータを読み込む
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    # 条件を満たす行を増殖させて新しいリストに追加する
    new_lines = []
    for line in lines:
        if '??' in line:
            with open('./input_list/prefecture_code_list_work.csv', 'r', encoding='utf-8') as file:
                for prefecture in file:
                    new_line = line.replace('??', prefecture[:2])
                    new_lines.append(new_line)
                    print(new_line)
        else:
            new_lines.append(line)
    # 新しいファイルに書き込む
    with open(output_file, 'w', encoding='utf-8') as file:
        file.writelines(new_lines)

### ファイルのダウンロード
def download_file(url, local_filename):
    try:
        # URLからファイルをダウンロードし、特定のローカルファイルパスに保存する
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return local_filename
    except requests.exceptions.HTTPError as e:
        print(f"HTTPエラーが発生しました: {e}")
    except IOError as e:
        print(f"ファイル書き込みエラーが発生しました: {e}")
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")
    return None

### 複数階層のZIPファイルを解凍
### ZIPファイルの中にZIPファイルがあるときは作業用フォルダに解凍
### ZIPファイル以外のファイルは特定のフォルダに解凍
# 使用例:
# zip_file_path = 'path/to/yourfile.zip'
# extract_to = 'path/to/destination_folder'
# work_folder = 'path/to/work_folder'
# other_files_folder = 'path/to/other_files_folder'
# extract_files(zip_file_path, extract_to, work_folder, other_files_folder)
def extract_files(zip_file_path, extract_to, work_folder, other_files_folder):
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        # ZIPファイル内のすべてのファイルを取得
        file_list = zip_ref.namelist()
        for file in file_list:
            file_path = os.path.join(extract_to, file)
            # フォルダの場合はスキップ
            if file.endswith('/'):
                continue
            # ZIPファイル以外のファイルを特定のフォルダに解凍
            if not file.endswith('.zip'):
                zip_ref.extract(file, other_files_folder)
            else:
                # ZIPファイルの場合は作業用フォルダに解凍
                nested_folder = os.path.join(work_folder, os.path.splitext(file)[0])
                os.makedirs(nested_folder, exist_ok=True)
                zip_ref.extract(file, nested_folder)
                # 作業用フォルダに解凍されたZIPファイルを再帰的に処理
                extract_files(os.path.join(nested_folder, file), nested_folder, work_folder, other_files_folder)


### 仮想にあるフォルダ内のデータをすべて最上層に移動
# 移動したいフォルダのパスを指定します
# folder_path = '/path/to/your/folder'
# move_folders_data_to_top(folder_path)
def move_files_to_parent_folder(folder_path):
    # フォルダ内のすべてのファイルを取得
    #root: 現在走査しているディレクトリのパスです。
    #dirs: そのrootディレクトリ内のディレクトリ名のリストです。
    #files: そのrootディレクトリ内のファイル名のリストです。
    for root, dirs, files in os.walk(folder_path):
        # ファイルを親フォルダに移動
        for file in files:
            # ファイルのパスを取得
            file_path = os.path.join(root, file)
            try:
                if folder_path != os.path.dirname(file_path):
                    shutil.move(file_path, folder_path)
            except shutil.Error as e:
                print(f"移動に失敗しました {file_path}: {e}")

### 指定のファイルからEPSGコードを返す
### ただし、ファイルにの先頭9文字は　EPSG:****　の書式を前提とする。
def return_EPSG( search_string,file_name):
    result = None
    search_prefix = search_string[:6]  # 検索文字列の先頭6文字を取得
    print(f"    {search_prefix}のEPSGコードを検索します。")
    with open(file_name, 'r', encoding='utf-8') as file:
        for line in file:
            if search_prefix in line:
                result = line[:9]
                print(f"    EPSGコードがありました：{result}")
                break
    return result

### 指定されたフォルダ内のすべてのShapefileの座標系を統一する関数。
# 使用例:
#folder_path = 'path/to/your/folder'
#target_epsg = 'EPSG:6668'
#unify_crs_in_folder(folder_path, target_epsg)
def unify_crs_in_folder(folder_path, target_epsg):
    non_crs_folder = os.path.join(folder_path, 'NON_CRS')
    os.makedirs(non_crs_folder, exist_ok=True)
    
    for file in os.listdir(folder_path):
        if file.endswith('.shp'):
            file_path = os.path.join(folder_path, file)
            # Shapefileを読み込む
            gdf = gpd.read_file(file_path, encoding='shift_jis')
            
            # 座標系が不明な場合の処理
            if gdf.crs is None:
                print(f"{file}のCRSが設定されていません。")
                EPSG_code = return_EPSG(file, "input_list/digital_national_land_information_url_list.txt")
                if EPSG_code == 'EPSG:****':
                    base_name, _ = os.path.splitext(file)
                    # 関連ファイルをNON_CRSフォルダに移動
                    related_files = [f"{base_name}.shp", f"{base_name}.shx", f"{base_name}.dbf", f"{base_name}.prj", f"{base_name}.cpg"]
                    for related_file in related_files:
                        related_file_path = os.path.join(folder_path, related_file)
                        if os.path.exists(related_file_path):
                            shutil.move(related_file_path, os.path.join(non_crs_folder, related_file))
                            print(f"    CRSが不明なため【処理対象外】とするため、ファイル {related_file} を NON_CRS フォルダに移動しました。")
                    continue
                else:
                    gdf.crs = EPSG_code
                    print(f"    SHPの現在のCRSを {EPSG_code} に設定しました。")
            # 座標系を統一する
            gdf = gdf.to_crs(target_epsg)
            # ファイルを上書き保存する
            gdf.to_file(file_path, encoding='shift_jis')
    print(f"すべてのShapefileを座標系【{gdf.crs}】に統一しました。")

### データ形式変換
#ESRI Shapefile: driver='ESRI Shapefile' (.shp)
#GeoPackage: driver='GPKG' (.gpkg)
#Keyhole Markup Language (KML): driver='KML' (.kml)
#GeoJSON: driver='GeoJSON' (.geojson)
#ただしCSVは以下で実行
#gdf.to_csv('output.csv')
# 使用例
#input_path = 'path/to/your/input_data.shp'
#output_path = 'path/to/your/output_data.gpkg'
#convert_format(input_path, output_path, input_format='ESRI Shapefile', output_format='GPKG')
def convert_format(input_path, output_path, input_format='ESRI Shapefile', output_format='GPKG'):
    # データを読み込む
    gdf = gpd.read_file(input_path)
    # 指定された出力フォーマットでファイルに保存する
    if output_format != 'csv':
        gdf.to_file(output_path, driver=output_format)
    else:
        gdf.to_csv(output_path)
    print(f"ファイルを変換しました：{output_path}")

###################################################################################

### 住居表示ファイルの取得及び結合
def address_download(file_name,combined_data_file):
# 初期化
    ### work/extracted_files　フォルダのクリーニング
    ### ※注意！　フォルダ内全ての一括処理があるため必ずその都度クリーニングを行うこと
    extracted_folder_path = 'work/extracted_files'
    if os.path.exists(extracted_folder_path):
        shutil.rmtree(extracted_folder_path)
    os.makedirs(extracted_folder_path)
    print(f"work/extracted_filesフォルダのクリーニングが完了しました。")

    ### 指定ファイル内のファイル一覧を読み込む
    # ファイルを読み込みモードで開く
    with open(file_name, "r") as file:
        # ファイルから行を1行ずつ読み込む
        file_list = file.readlines()
    # 各行の末尾の改行文字を削除
    file_list = [line.strip() for line in file_list]

    ### 読み込んだファイル一覧を順次処理
    for file_path in file_list:
        print(file_path)
        ### ファイルのダウンロード
        url = file_path
        local_filename = 'work/download.zip'
        download_file(url, local_filename)
        ### ダウンロードしてZIPファイルを読み込みモードで開き解凍
        with zipfile.ZipFile(local_filename, 'r') as my_zip:
            # ZIPファイル内のファイル一覧を表示
            file_list = my_zip.namelist()
            print("ZIPファイル内のファイル一覧:")
            for file_name in file_list:
                print(f"　　・{file_name}")
            # ZIPファイル内の全てのファイルを解凍
            my_zip.extractall('work/extracted_files')
            ### 所定のフォルダ内のすべてのCSVファイルを結合
            ### 最初のファイルの属性行を取得しそれ以降のファイルの属性行は無視
            # CSVファイルが保存されているディレクトリを指定
            csv_directory = 'work/extracted_files'
            # 最初のCSVファイルから列名を取得
            first_file = os.listdir(csv_directory)[0]
            first_file_path = os.path.join(csv_directory, first_file)
            first_df = pd.read_csv(first_file_path)
            column_names = first_df.columns.tolist()
            # 結合するための空のDataFrameを作成
            combined_data = pd.DataFrame(columns=column_names)
            # 指定したディレクトリ内のCSVファイルを結合
            for filename in os.listdir(csv_directory):
                if filename.endswith(".csv"):
                    file_path = os.path.join(csv_directory, filename)
                # 全ても文字列として読み込むように明示
                df = pd.read_csv(file_path, dtype=str)
                # 列名を引き継いで結合
                combined_data = pd.concat([combined_data, df], ignore_index=True)
                # 結合したデータを1つのCSVファイルに保存
                combined_data.to_csv(combined_data_file, index=False)
            print(f"CSVファイルの結合が完了しました。")

    ### CSVファイルを文字列として読み込む
    df = pd.read_csv(combined_data_file,dtype=str)
    # 結合したい文字列の属性を選択し、新しい文字列の属性を作成する
    df['街区ユニークid'] = df['全国地方公共団体コード'] + df['町字id'] + df['街区id']
    # 新しいCSVファイルに保存する
    df.to_csv(combined_data_file, index=False)
    print(f"街区ユニークidを追加しました。")
    return

### geoファイルの取得及び各県のデータを１ファイルに結合
# 先頭に#があるときはスキップ　コメントアウト
def geo_download(file_name):
    try:
        # 読み込み専用ファイルへの変換
        ###############################################################
        # ファイルの中にある??を01－47の連番にして新しいファイルを作成する #
        ###############################################################
        work_file_name = file_name + '.work'
        process_file(file_name, work_file_name)
        print(f"作業用ファイル {work_file_name} を作成しました。")

        # 指定ファイル内のファイル一覧を読み込む
        with open(work_file_name, "r", encoding='UTF-8') as file:
            file_list = file.readlines()

        file_list = [line.strip() for line in file_list]

        #################################
        # 読み込んだファイル一覧を順次処理 #
        #################################
        for line in file_list:
            line = line.strip()

            # 行の先頭が '#' の場合はスキップ
            if line.startswith('#'):
                continue

            # ',' がデリミタとして使われていると仮定
            if ',' in line:  
                EPSG_code, file_path, file_title = line.split(',')
                EPSG_code = EPSG_code.strip()
                file_path = file_path.strip()
                file_title = file_title.strip()
                print(f"EPSG_code: {EPSG_code}, ファイルパス: {file_path}, タイトル: {file_title}")
            else:
                file_path = line
                print(f"ファイルパス: {file_path}")

            # ファイルのダウンロード
            
            url = file_path
            local_filename = 'work/download.zip'
            download_file(url, local_filename)

            # ZIPファイル内の全てのファイルを解凍
            zip_file_path = 'work/download.zip'
            extract_to = 'work/extracted_files'
            work_folder = 'work/work_folder'
            other_files_folder = 'work/other_files_folder'
            extract_files(zip_file_path, extract_to, work_folder, other_files_folder)
            print(f"ZIPファイルの解凍が完了しました。")

        # 仮想にあるフォルダ内のデータをすべて最上層に移動
        folder_path = 'work/other_files_folder'
        print(f"{folder_path}の下層にフォルダがある場合はすべて直下に移動します。")
        move_files_to_parent_folder(folder_path)

    except UnicodeDecodeError as e:
        print(f"UnicodeDecodeError: {e}")
        # エラーが発生した場合の処理をスキップする

    return


def replace_attributes(folder_path, csv_file_path):
    # フォルダ内のすべてのGPKGファイルに対して処理を行う
    for filename in os.listdir(folder_path):
        if filename.endswith(".gpkg"):
            # GPKGファイルを読み込む
            gpkg_path = os.path.join(folder_path, filename)
            gdf = gpd.read_file(gpkg_path)

            # CSVファイルを読み込む
            csv_data = pd.read_csv(csv_file_path)

            # 属性の置き換えを行う
            for index, row in csv_data.iterrows():
                shp_attribute_name = row['shp属性名']
                attribute_name = row['属性名']

                if shp_attribute_name in gdf.columns:
                    gdf[attribute_name] = gdf[shp_attribute_name]
                    gdf = gdf.drop(columns=[shp_attribute_name])

            # 置き換えたデータを新しいGPKGファイルとして保存
            new_gpkg_path = os.path.join(folder_path, filename)
            gdf.to_file(new_gpkg_path, driver='GPKG')
            print(f"{filename}の属性をコードから日本語に置き換えました。")

### フォルダ内のすべてのSHPにジオメトリの経度X、緯度Y座標属性値を追加
def add_coordinates_to_shapefiles(folder_path):
    # フォルダ内のすべての Shapefile ファイルを処理
    for filename in os.listdir(folder_path):
        if filename.endswith(".shp"):
            # Shapefile ファイルのパスを構築
            shp_path = os.path.join(folder_path, filename)
            
            # GeoDataFrame を読み込む
            gdf = gpd.read_file(shp_path)
            
            # ジオメトリから 緯度と経度を取得
            gdf['緯度'] = gdf.geometry.y
            gdf['経度'] = gdf.geometry.x
            
            # 新しい属性を付加した GeoDataFrame を保存
            gdf.to_file(shp_path, encoding='shift_jis')
            print(f"ファイル{shp_path}にジオメトリより経度X、緯度Y座標属性値を追加しました。")

### フォルダ内のすべてのSHPファイルをGPKGにコンバート
def convert_shp_to_gpkg(input_folder, output_folder):
    # SHPファイルが格納されている入力フォルダ
    shp_files = [f for f in os.listdir(input_folder) if f.endswith('.shp')]
    # GPKGファイルの出力フォルダ
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    for shp_file in shp_files:
        shp_path = os.path.join(input_folder, shp_file)
        # .shpを.gpkgに置き換えてGPKGファイル名を作成
        gpkg_file = os.path.splitext(shp_file)[0] + '.gpkg'
        gpkg_path = os.path.join(output_folder, gpkg_file)
        # Geopandasを使用してSHPファイルを読み込む
        gdf = gpd.read_file(shp_path)
        # GeoPackageに書き込む
        gdf.to_file(gpkg_path, driver='GPKG')
        print(f"{shp_file} を {gpkg_file} に変換しました")


### フォルダ内のすべてのジオメトリをPOINTに変更
def convert_geometries_to_points(folder_path):
    # フォルダ内のgpkgファイルを取得
    gpkg_files = [f for f in os.listdir(folder_path) if f.endswith('.gpkg')]
    for gpkg_file in gpkg_files:
        file_path = os.path.join(folder_path, gpkg_file)
        # GeoDataFrameを読み込む
        gdf = gpd.read_file(file_path)
        # ジオメトリを変換
        gdf['geometry'] = gdf['geometry'].apply(convert_geometry)
        # 変換後のGeoDataFrameを保存
        output_file_path = os.path.join(folder_path, f"{gpkg_file}")
        gdf.to_file(output_file_path, driver='GPKG')
# ジオメトリをポイントに変換する関数
def convert_geometry(geom):
    if geom.geom_type == 'LineString':
        # ラインの中心を取得して新しいジオメトリを作成
        new_geom = LineString([geom.centroid])
        print(f"ラインをポイントに変換しました。")
    elif geom.geom_type == 'Polygon':
        # ポリゴンの重心を取得して新しいジオメトリを作成
        new_geom = Point(geom.centroid)
        print(f"ポリゴンをポイントに変換しました。")
    else:
        # その他のジオメトリはそのまま保持
        new_geom = geom
    return new_geom

### フォルダ内のすべてのgpkgファイルをマージします。
# フォルダ内のすべてのgpkgファイルをマージする関数
def merge_geopackages(input_folder, output_file):
    try:
        print(f"{input_folder}フォルダ内のすべてのgpkgファイルをマージして、{output_file}に保存します。")
        # フォルダ内のgpkgファイルをソートして取得
        gpkg_files = sorted([f for f in os.listdir(input_folder) if f.endswith('.gpkg')])
        # ファイルが存在しない場合はエラーを発生させる
        if not gpkg_files:
            raise ValueError("フォルダ内にGeoPackageファイルが見つかりません。")
        # 初期化
        merged_gdf = None
        # 各GeoPackageファイルを順番に処理
        for gpkg_file in gpkg_files:
            # 各GeoPackageファイルを読み込む
            input_path = os.path.join(input_folder, gpkg_file)
            gdf_to_merge = gpd.read_file(input_path)
            # マージを実行
            if merged_gdf is None:
                # 最初のファイルをベースとして使用
                merged_gdf = gdf_to_merge.copy()
                print(f"{gpkg_file} をベースファイルとして読み込みました。")
            else:
                # 既存のGeoDataFrameとマージ
                merged_gdf = gpd.GeoDataFrame(pd.concat([merged_gdf, gdf_to_merge], ignore_index=True))
                print(f"{gpkg_file} をマージしました")
        # マージしたデータを一つのGeoPackageファイルに保存
        merged_gdf.to_file(output_file, driver="GPKG")
        print(f"マージしたデータを {output_file} に保存しました")
        print("全てのファイルのマージと保存が完了しました。")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

def add_city_name(gpkg_file, csv_file):
    # CSVデータを事前に読み込む
    csv_data = pd.read_csv(csv_file, encoding='UTF-8', delimiter=',', dtype=str)
    csv_data = csv_data[['改正後のコード', '最終市区町村名', '都道府県名（漢字）']]
    
    # GeoPackageファイルを読み込む
    gdf = gpd.read_file(gpkg_file, dtype=str)
    
    # 必要な列が存在しない場合は追加する
    if '所在地_市区町村' not in gdf.columns:
        gdf['所在地_市区町村'] = None
    if '所在地_都道府県' not in gdf.columns:
        gdf['所在地_都道府県'] = None

    # '改正後のコード'の重複を削除し、データの重複を事前に処理
    csv_data_unique = csv_data.drop_duplicates(subset=['改正後のコード'])

    # GeoPackageのデータとCSVデータをマージして補完処理を行う
    gdf = gdf.merge(csv_data_unique, left_on='国土数値情報用行政区域コード', right_on='改正後のコード', how='left')
    # NULLの場合は補完値を使用する
    gdf['所在地_市区町村'] = gdf['所在地_市区町村'].fillna(gdf['最終市区町村名'])
    gdf['所在地_都道府県'] = gdf['所在地_都道府県'].fillna(gdf['都道府県名（漢字）'])
    
    # 不要な列を削除する
    gdf.drop(columns=['改正後のコード', '最終市区町村名', '都道府県名（漢字）'], inplace=True)
    
    # 更新されたデータをGeoPackageファイルに書き込む
    gdf.to_file(gpkg_file, driver='GPKG')
    print("[所在地_都道府県][所在地_市区町村]を補完しました。")


def change_new_city_code(gpkg_file, csv_file):
    # CSVデータを事前に読み込む
    csv_data = pd.read_csv(csv_file, encoding='UTF-8', delimiter=',', dtype=str)
    # 必要な列を選択
    csv_data = csv_data[['行政区域コード', 'コードの改定区分', '改正後のコード']]
    # 'コードの改定区分'列が'欠番'の行を抽出
    csv_data = csv_data[csv_data['コードの改定区分'] == '欠番']
    print(f"欠番コード\n{csv_data}")
    # GeoPackageファイルを読み込む
    gdf = gpd.read_file(gpkg_file, dtype=str)
    
    # '行政区域コード'の重複を削除し、データの重複を事前に処理
    csv_data_unique = csv_data.drop_duplicates(subset=['行政区域コード'])

    # GeoPackageのデータとCSVデータをマージして補完処理を行う
    gdf = gdf.merge(csv_data_unique, left_on='国土数値情報用行政区域コード', right_on='行政区域コード', how='left')

    # 欠番の場合、国土数値情報用行政区域コードに改正後のコードを代入する
    gdf.loc[gdf['コードの改定区分'] == '欠番', '国土数値情報用行政区域コード'] = gdf['改正後のコード']
    # 不要な列を削除する
    gdf.drop(columns=['行政区域コード', 'コードの改定区分', '改正後のコード'], inplace=True)
    
    # 更新されたデータをGeoPackageファイルに書き込む
    gdf.to_file(gpkg_file, driver='GPKG')
    print("[国土数値情報用行政区域コード]欠番が入力されているデータを最新[国土数値情報用行政区域コード]に修正しました。")
