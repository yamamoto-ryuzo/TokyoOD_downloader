# TokyoOD_downloader
  [本体はこちらからダウンロードも可能で（ちょっと古いこともあるかも。。。）](https://1drv.ms/u/c/cbbfeab49e70546f/EUECp2yGUGFGumAZdLTmtbgB8cbhqMfqGFLh-nrMJ1O9yw?e=UFrj23)  
## 最終目標  
[東京都オープンデータカタログサイト](https://portal.data.metro.tokyo.lg.jp/)からオープンデータ一覧をダウンロードして、CSVデータのうち位置情報のあるデータを抽出し、ダウンロードしたデータは以下でPostgRESTとして公開予定。（サーバーの能力の問題から東京都、目黒区のみです。）  
　https://github.com/yamamoto-ryuzo/PostgREST-installation-Japanese-memo/blob/main/使用方法.md  
#### 【動作フロー】  
　 データ検索　＞　カタログデータ一覧取得　＞　実データ一括ダウンロード  
#### 【CSVのみの追加フロー】  
　 UTF-8の文字コード統一　＞　座標データを仕訳（EPSG：4326と仮定）　＞　ファイルの統合　＞　GPKG作成  
## 東京都オープンデータカタログサイトの仕様
#### 取得可能データ属性
データセットID,データセットタイトル,データセット説明,タグ, タグ（読み）,ライセンス,組織,事業説明等のページ,  
データ所管部署,データセット作成日時,データセット最終更新日時,更新頻度,カテ ゴリ（分類）,データタイトル,  
データURL,データ説明,形式,サイズ,並び順,データ作成日時,データ最終更新日時  
## 仕様
　・対応ファイル形式  
 　　　CSV（CSV以外の形式はダウンロードまで可能。。。たぶん。。。動作確認してません。）  
　・文字コードは　UTF-8　に統一   
　・CSVデータをダウンロードした場合、座標値を含むものとそうでないものも仕分け  
　　　　　座標値あり：GIS_元のファイル名  
　　　　　座標値なし：NON_元のファイル名  
　・EPSG:4326 - WGS 84  
## 利用方法
以下を同じフォルダに設置してください。  
　　本体：TokyoOD_downloder.exe  
作成されるフォルダ  
　　ダウンロードする予定のURL一覧：./download/dataURLList.csv  
　　ダウンロードしたデータ本体：./dowqnload/data 
　　※注意　毎回起動時に自動削除します。
## 画面入力（サンプルが入っています）  
organization:t131105 title:トイレ  
　　　↑目黒区のコード　 　↑「title:検索対象」データセットタイトルで検索  
datatype=csv  
![image](https://github.com/user-attachments/assets/f9259dc0-21fd-43bc-800f-a24d5ea3a2cc)


## 出力サンプル
#### マージデータ：  
　ルートフォルダにマージファイルは作成されます  
　作成されるファイルはGISデータをもつCSVファイル、GPKGファイル    
 ![image](https://github.com/user-attachments/assets/d4492a6c-235a-4b7b-8afd-80cac6fee418)  
#### ダウンロードする予定のURL一覧：./download/dataURLList.csv  
![image](https://github.com/user-attachments/assets/a012f566-d355-4aea-88b9-3fdceaec13ed)  
#### ダウンロードしたデータ本体：./dowqnload/data    
![image](https://github.com/user-attachments/assets/8f9b572f-86dc-41ef-9ee1-fc9149c32b15)  
