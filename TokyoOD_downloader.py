"""
【仮想環境】
VS Codeの設定で、Pythonインタープリタが正しく設定されているか確認してください。
コマンドパレット（Ctrl + Shift + P）を開き
「Python: Select Interpreter」を選択し、正しいPython環境を選択します。

1.PowerShellを管理者権限で実行
2.現在の実行ポリシーを確認
    Get-ExecutionPolicy
3.実行ポリシーを変更
    Set-ExecutionPolicy RemoteSigned
4.仮想環境にもどって、アクティブ化
5.仮想環境のアクティベーション
    .\.venv\Scripts\activate

【仮想環境へインストールモジュール】
pip install geopandas requests fiona chardet

【履歴概要】
#2024/08/18 作成開始　とりあえず一覧取得から
"""

import geopandas as gpd
import pandas as pd
import shutil
import os
import requests
import chardet
import io
from charset_normalizer import detect

###########################################
######## 自作関数ファイルを読み込み #########
###########################################

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
    url = "https://catalog.data.metro.tokyo.lg.jp/csv/export"
    # データセットタイトル
    title = "title:トイレ一覧"
    # データセット説明文
    res_description = "res_description:トイレ"
    q = title
    format = "csv"
    df = fetch_data_from_url(url, q, format)

    #if df is not None:
    #    print(df)

    ######## データアドレスを必要な属性のみ保存 #########
    columns_to_select = ['データセットID','データURL']
    file_path="./download/dataURLList.csv"
    download_DataURL(df,columns_to_select,file_path)  

    ######## 実際のデータをダウンロード #########
    # ファイルの存在を確認
    if os.path.exists(file_path):
        # CSVファイルを読み込む
        data = pd.read_csv(file_path)

        # データURLが含まれている列を特定（ここでは'URL'という列名を仮定）
        if 'データURL' in data.columns:
            attribute_urls = data['データURL'].dropna().tolist()
        else:
            attribute_urls = []
            print("CSVファイルに'URL'という列が見つかりません。")

        ######## 各URLからデータをダウンロード ########
        ######## 領域のクリア #########
        download_dir = "./download/data/"
        #clean_work_folder(download_dir)

        for url in attribute_urls:
            try:
                #属性に緯度経度があればflag=1とする
                GISFlag=0
                response = requests.get(url)
                response.raise_for_status()  # ステータスコードがエラーの場合は例外を発生

                # コンテンツをファイルに保存
                file_name = url.split('/')[-1]  # URLの最後の部分をファイル名として使用
                with open(f'{download_dir+file_name}', 'wb') as file:
                    file.write(response.content)
                print(f"ダウンロード完了: {download_dir+file_name}")

                ######## Shift-JIS確認 #########
                # バイナリモードでファイルを開く
                with open(f'{download_dir+file_name}', 'rb') as f:
                    # ファイルの内容を読み込む
                    content = f.read()
                    # エンコーディングを判定
                    result = chardet.detect(content)
                    # 判定結果を表示
                    print(f"Encoding: {result['encoding']}, Confidence: {result['confidence']}")

                ######## Shift-JISの場合UTF-8に変換 #########
                if result['encoding'] == 'SHIFT_JIS':
                    # Shift-JISで読み込み、UTF-8で書き出す
                    with open(f'{download_dir+file_name}', 'r', encoding='shift_jis') as f:
                        text = f.read()
                    with open(f'{download_dir+file_name}', 'w', encoding='UTF-8') as f:
                        f.write(text)
                    print(f"{download_dir+file_name}をUTF-8に変換しました。")
                ######## UTF-8-SIG(BOM付き)の場合UTF-8に変換 #########
                if result['encoding'] == 'UTF-8-SIG':
                    # Shift-JISで読み込み、UTF-8で書き出す
                    with open(f'{download_dir+file_name}', 'r', encoding='UTF-8-SIG') as f:
                        text = f.read()
                    with open(f'{download_dir+file_name}', 'w', encoding='UTF-8') as f:
                        f.write(text)
                    print(f"{download_dir+file_name}をUTF-8に変換しました。")
                ######## 緯度列の確認 #########
                # UTF-8で再度CSVを読み込む
                    data = pd.read_csv(f'{download_dir+file_name}', encoding='UTF-8')
                    if '緯度' in data.columns:
                        # ファイル名の先頭にGIS_を付け加える
                        new_file_name = os.path.join(download_dir, f"GIS_{file_name}")
                        print(f" {file_name} :位置情報があります。")
                    else:
                        # ファイル名の先頭にNON_を付け加える
                        new_file_name = os.path.join(download_dir, f"NON_{file_name}")
                        print(f" {file_name} :位置情報がありません。")
                    force_rename(f'{download_dir+file_name}', new_file_name)
                    print(f"ファイル名を変更しました: {file_name} -> {new_file_name}")

            except requests.exceptions.RequestException as e:
                print(f"{url}のダウンロードに失敗しました: {e}")
    else:
        print(f"ファイルが見つかりません: {file_path}")

# エラー処理
except FileNotFoundError:
    print(f"ファイルが見つかりません。")
except Exception as e:
    print(f"エラーが発生しました: {e}")