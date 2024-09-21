# 【仮想環境】
# VS Codeの設定で、Pythonインタープリタが正しく設定されているか確認してください。
# コマンドパレット（Ctrl + Shift + P）を開き
# 「Python: Select Interpreter」を選択し、正しいPython環境を選択します。
#
# 1.PowerShellを管理者権限で実行
# 2.現在の実行ポリシーを確認
#     Get-ExecutionPolicy
# 3.実行ポリシーを変更
#     Set-ExecutionPolicy RemoteSigned
# 4.仮想環境にもどって、アクティブ化
# 5.仮想環境のアクティベーション
#     .\.venv\Scripts\activate
#
# 【仮想環境へインストールモジュール】
# pip install geopandas requests fiona chardet ftfy pathvalidate
#
# 【履歴概要】
# 2024/08/18 作成開始　とりあえず一覧取得から
# 2024/08/22 CSVマージおよびGPKG作成を選択できるように修正

import geopandas as gpd
import pandas as pd
import shutil
import os
import requests
import chardet
import io
from charset_normalizer import detect
from shapely.geometry import Point
import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
import ftfy
from pathvalidate import sanitize_filename
from urllib.parse import urlparse, unquote

#########独自関数
import csv_convert,xls2csv

###########################################
######## 自作関数ファイルを読み込み #########
###########################################

######## コンフィグ入力画面 #########
import tkinter as tk

def input_config():
    # グローバル変数を使用して値を保存
    global search_query, data_format, selected_urls

    # メインウィンドウを作成
    root = tk.Tk()
    root.title('入力フォーム')  # ウィンドウタイトルを設定
    
    # ウィンドウサイズを設定
    window_width = 700
    window_height = 250
    root.geometry(f"{window_width}x{window_height}")
    
    # フレームを作成して配置
    frame = tk.Frame(root)
    frame.pack(anchor='w', padx=20, pady=20)  # 左寄せ
    
    # URL選択用のOptionMenuを作成
    tk.Label(frame, text='カタログサイトURLを選択してください:').grid(row=0, column=0, padx=5, pady=5, sticky='w')
    url_var = tk.StringVar(value="https://catalog.data.metro.tokyo.lg.jp/csv/export")  # デフォルト値
    url_options = [
        "https://catalog.data.metro.tokyo.lg.jp/csv/export",
    ]
    url_menu = tk.OptionMenu(frame, url_var, *url_options)
    url_menu.grid(row=0, column=1, padx=5, pady=5, sticky='w')

    # データ形式選択用のOptionMenuを作成
    tk.Label(frame, text='データ形式を選択してください:').grid(row=1, column=0, padx=5, pady=5, sticky='w')
    data_type_var = tk.StringVar(value='CSV')  # デフォルト値
    data_type_options = ['CSV', 'SHP', 'GEOJSON', 'PDF', 'XLSX', 'JPEG', 'XLS', 'ZIP']
    data_type_menu = tk.OptionMenu(frame, data_type_var, *data_type_options)
    data_type_menu.grid(row=1, column=1, padx=5, pady=5, sticky='w')

    # 手動入力用のエントリを作成
    tk.Label(frame, text='データ形式を手入力で指定:').grid(row=2, column=0, padx=5, pady=5, sticky='w')
    manual_data_type_entry = tk.Entry(frame, width=20)
    manual_data_type_entry.grid(row=2, column=1, padx=5, pady=5, sticky='w')     

    # 検索入力用のラベルとエントリを作成
    tk.Label(frame, text='検索対象を入力:').grid(row=3, column=0, padx=5, pady=5, sticky='w')
    search_entry = tk.Entry(frame, width=70) 
    search_entry.grid(row=3, column=1, padx=5, pady=5, sticky='w')

    # デフォルトの検索値を挿入
    search_default = 'organization:t131105 title:トイレ'
    search_entry.insert(0, search_default)
    
    # 送信ボタンのクリック時の処理
    def submit():
        global search_query, data_format, selected_urls
        search_query = search_entry.get()
        data_format = manual_data_type_entry.get() or data_type_var.get()
        data_format = data_format.upper()
        
        # 選択されたURLを取得
        selected_urls = url_var.get()
        
        root.quit()  # mainloopを終了

    # 送信ボタンを作成
    submit_button = tk.Button(frame, text='送信', command=submit)
    submit_button.grid(row=4, column=1, pady=10, sticky='e')  # 右寄せ
    
    # Tkinterのイベントループを開始
    root.mainloop()
    root.destroy()  # ウィンドウを閉じる
    
    # 検索クエリ、データ形式、選択されたURLを返す
    return search_query, data_format, selected_urls

# 使用例
# search_query, data_format, selected_urls = input_config()
# print("検索クエリ:", search_query)
# print("データ形式:", data_format)
# print("選択されたURL:", selected_urls)

######## はい・いいえのダイアログ #########
def show_confirmation_dialog(title, message):
    """
    確認ダイアログを表示し、ユーザーの応答を返す。

    Parameters:
    title (str): ダイアログのタイトル。
    message (str): ダイアログに表示するメッセージ。

    Returns:
    bool: ユーザーが「はい」を選択した場合はTrue、それ以外はFalse。
    """
    # Tkinterのルートウィンドウを作成
    root = tk.Tk()
    # メインウィンドウを非表示にする 
    root.withdraw()  
    # 確認ダイアログを表示
    result = messagebox.askyesno(title, message)
    return result

######## URLからリストを抽出 #########
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
        response.encoding = "UTF-8"
        
        # データをDataFrameとして読み込む
        df = pd.read_csv(io.BytesIO(response.content), encoding=response.encoding)
        return df
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        return None
"""
【使用例】
url = "https://catalog.data.metro.tokyo.lg.jp/csv/export"
q = "トイレ"
format = "CSV"

df = fetch_data_from_url(url, q, format)
if df is not None:
    print(df)
"""
######## URLから適切なファイル名を生成 #########
def get_safe_filename_from_url(url):
    parsed_url = urlparse(url)
    unsafe_filename = os.path.basename(unquote(parsed_url.path))
    return sanitize_filename(unsafe_filename)

######## URLのファイルをダウンロード #########
def download_DataURL(df, columns_to_select, output_file):
    # DataURLの列を抽出
    DataURL = df[columns_to_select]
    # URLをCSVファイルに保存
    DataURL.to_csv(output_file, index=False, encoding='UTF-8')

# 使用例
# 'df'DataFrameで、'データURL'がデータのURLを含む列名であると仮定
# download_DataURL(df, 'データURL', 'data.csv')

######## ファイルの強制リネーム #########
def force_rename(src, dst):
    # 目的のファイルが既に存在する場合、削除する
    if os.path.exists(dst):
        os.remove(dst)  # 既存のファイルを削除
    os.rename(src, dst)  # ファイルをリネーム
    print(f'{src}を{dst}に強制上書きしました。')

    # 元のファイルが残っているか確認し、削除する
    if os.path.exists(src):
        os.remove(src)
        print(f'元のファイルを削除しました: {src}')
    else:
        print(f'元のファイルが存在しません: {src}')

########フォルダのクリーニング ########
#work_folder_path = 'work'
#clean_work_folder(work_folder_path)
def clean_work_folder(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    os.makedirs(folder_path)
    print(f"{folder_path}フォルダのクリーニングが完了しました。")

########名称にデータを統一########
def load_and_modify_csv(download_dir, file_name):
    file_path = os.path.join(download_dir, file_name)
    try:
        # CSVファイルを読み込む
        data = pd.read_csv(file_path, encoding='UTF-8', on_bad_lines='skip')

        # すべてのデータがない行を削除する
        data = data.dropna(how='all')
        
        # '名称'カラムが存在しない場合のみ、他のカラムをチェックし、'名称'カラムを作成
        if '名称' not in data.columns:
            # '名称', '*名称*', 'NAME'カラムの存在をチェックし、'名称'カラムを作成
            name_columns = ['NAME', '施設名', '保育園名','鉄道駅名']
            for col in name_columns:
                if col in data.columns:
                    data['名称'] = data[col]
                    break
        # 変更を上書き保存
        data.to_csv(file_path, index=False, encoding='UTF-8')
        print(f"{file_name} : ファイルが上書き保存されました。")
    
    except FileNotFoundError:
        print(f"エラー: ファイルが見つかりません - {file_path}")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

# 使用例
#download_dir = '/path/to/download'
#file_name = 'example.csv'
#load_and_modify_csv(download_dir, file_name)



#########################
######## メイン #########
########################
"""
取得可能データ属性
データセットID,データセットタイトル,データセット説明,タグ, タグ（読み）,ライセンス,組織,事業説明等のページ,データ所管部署,データセット作成日時
,データセット最終更新日時,更新頻度,カテ ゴリ（分類）,データタイトル,データURL,データ説明,形式,サイズ,並び順,データ作成日時,データ最終更新日時

（出力例）
okyo.lg.jp/seisaku/details/awareness_survey.html,スポーツ総合推進部パラスポーツ課,2024/04/19 11:34:38,2024/04/19 11:35:11,年次,生活
,デフリンピックに期待すること,https://www.opendata.metro.tokyo.lg.jp/seikatubunka/Q32_dehurinpikkunikitaisurukoto.csv
,上記の設問に係る単純集計表及びクロス集計表です。,CSV,39KB,39,2024/03/19 15:37:00,2024/03/19 15:37:00

【検索例 未検証　エラー中：現在事務局に引数を問い合わせ中】
https://catalog.data.metro.tokyo.lg.jp/dataset?q=title:データセットタイトル+AND+res_description:データセット説明文+AND+tags:タグ+AND+metadata_modified:[2024-09-20T00:00:0.000Z TO 2024-09-21T23:59:0.000Z]
https://catalog.data.metro.tokyo.lg.jp/dataset?q=title:トイレ一覧+AND+res_description:トイレ
"""

try:
    ######## データアドレス一覧取得 #########
    # データセットタイトル
    search, data_type , url = input_config()
    print(f"search: {search}")
    print(f"data_type: {data_type}")
    print(f"url: {url}")
    q = search
    df = fetch_data_from_url(url, q, data_type)
    if df is not None:
        print(df)

    ######## ダウンロードフォルダの作成 #########
    # ディレクトリのパスを指定
    directory_path = './data/'+ data_type
    print (f"保存先ディレクトリ：{directory_path}")
    # ディレクトリが存在する場合に削除
    try:
        if os.path.exists(directory_path):
            shutil.rmtree(directory_path)
    except Exception as e:
        print(f"ディレクトリの削除中にエラーが発生しました: {e}")
    # ディレクトリが存在しない場合に作成
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

    ######## データアドレスを必要な属性のみ保存 #########
    columns_to_select = ['データセットID','データURL','データセットタイトル']
    file_path="./data/dataURLList.csv"
    download_DataURL(df,columns_to_select,file_path)  

    ######## 実際のデータをダウンロード #########
    # ファイルの存在を確認
    if os.path.exists(file_path):
        # ダウンロードするファイルリストの記載されたCSVファイルを読み込む
        data = pd.read_csv(file_path)

        # データURLが含まれている列を特定（ここでは'URL'という列名を仮定）
        if 'データURL' in data.columns:
            attribute_urls = data['データURL'].dropna().tolist()
        else:
            attribute_urls = []
            print("CSVファイルに'URL'という列が見つかりません。")

        ######## 各URLからデータをダウンロード ########
        ######## 領域のクリア #########
        download_dir = directory_path
        #clean_work_folder(download_dir)

        for url in attribute_urls:
            try:
                #属性に緯度経度があればflag=1とする
                GISFlag=0
                response = requests.get(url)
                response.raise_for_status()  # ステータスコードがエラーの場合は例外を発生

                ######## コンテンツをファイルに保存（ダウンロード） #########
                file_name = get_safe_filename_from_url(url) #適切なファイル名を取得
                with open(f'{download_dir+'/'+file_name}', 'wb') as file:
                    file.write(response.content)
                print(f"--------------------------ダウンロード完了: {download_dir+'/'+file_name}")

            except requests.exceptions.RequestException as e:
                print(f"{url}のダウンロードに失敗しました: {e}")
    else:
        print(f"ファイルが見つかりません: {file_path}")


    ######## XLSデータの場合の処理 #########
    if data_type == 'XLS':
        input_directory = directory_path
        output_directory = './data/csv'
        xls2csv.process_excels_in_batches(input_directory, output_directory)
        data_type = 'CSV'

    ######## CSVデータの場合の処理 #########
    if data_type == 'CSV':
        ######## CSVのデータコンバート #########
        input_directory = './data/'+ data_type
        output_directory = './data/csv_convert'
        csv_convert.process_csv_files(input_directory, output_directory)
        ######## すべてのファイルをマージするかどうかの判断 #########
        # 確認ダイアログを表示
        title = "GIS_CSVのマージ・GPKGの作成"
        message = "データによっては非常に所持時間が必要ですがよろしいですか。"
        user_response = show_confirmation_dialog(title, message)

        # ユーザーの応答に基づいて処理を行う
        if user_response:
            # 「はい」が選択された場合の処理
            ######## すべてのファイルをマージする #########
            # マージする’CSVファイルを格納するリスト
            csv_files = []
            
            # ディレクトリ内のファイルを取得
            for filename in os.listdir(directory_path):
                if filename.startswith('GIS_') and filename.endswith('.csv'):
                    csv_files.append(os.path.join(directory_path, filename))

            # CSVファイルを読み込み、データフレームをリストに追加
            dataframes = [pd.read_csv(csv_file, low_memory=False) for csv_file in csv_files]

            # データフレームをマージ
            merged_df = pd.concat(dataframes, ignore_index=True)

            # マージしたデータをCSVファイルとして保存
            merged_csv_path = "./GIS_merge_csv.csv"
            merged_df.to_csv(merged_csv_path, index=False)

            # '緯度'を数値に変換し、エラーをNaNに変換
            merged_df['緯度'] = pd.to_numeric(merged_df['緯度'], errors='coerce')

            # '緯度'がNaNの行を削除
            filtered_df = merged_df.dropna(subset=['緯度'])

            # 'geometry'列を作成
            filtered_df['geometry'] = filtered_df.apply(lambda row: Point(row['経度'], row['緯度']), axis=1)

            # GeoDataFrameに変換
            gdf = gpd.GeoDataFrame(filtered_df, geometry='geometry', crs='EPSG:4326')

            # GPKGファイルとして保存
            gpkg_path = "./GIS_merge.gpkg"
            gdf.to_file(gpkg_path, driver='GPKG')

# エラー処理
except FileNotFoundError:
    print(f"ファイルが見つかりません。")
except Exception as e:
    print(f"エラーが発生しました: {e}")