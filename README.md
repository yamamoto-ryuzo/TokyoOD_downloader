# TokyoOD_downloader
## 最終目標  
[東京都オープンデータカタログサイト](https://portal.data.metro.tokyo.lg.jp/)からオープンデータ一覧をダウンロードして、CSVデータのうち位置情報のあるデータを抽出し、ダウンロードしたデータは以下でPostgRESTとして公開予定。（サーバーの能力の問題から東京都、目黒区のみです。）  
　https://github.com/yamamoto-ryuzo/PostgREST-installation-Japanese-memo/blob/main/使用方法.md  
## 東京都オープンデータカタログサイトの仕様
#### 取得可能データ属性
データセットID,データセットタイトル,データセット説明,タグ, タグ（読み）,ライセンス,組織,事業説明等のページ,  
データ所管部署,データセット作成日時,データセット最終更新日時,更新頻度,カテ ゴリ（分類）,データタイトル,  
データURL,データ説明,形式,サイズ,並び順,データ作成日時,データ最終更新日時  
## 仕様
　・対応ファイル形式  
 　　　CSV  
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
      ↑マージとかはCSVしか対応していません、ダウンロードだけなら他の形式もそれなりにエラー出しながらOKです！（たぶん。。。）
![image](https://github.com/user-attachments/assets/1c0471c7-5078-4708-a961-07ee8a764730)

## 出力サンプル
#### マージデータ：  
　ルートフォルダにマージファイルは作成されます  
　作成されるファイルはGISデータをもつCSVファイル、GPKGファイル    
 ![image](https://github.com/user-attachments/assets/d4492a6c-235a-4b7b-8afd-80cac6fee418)  
#### ダウンロードする予定のURL一覧：./download/dataURLList.csv  
![image](https://github.com/user-attachments/assets/a012f566-d355-4aea-88b9-3fdceaec13ed)  
#### ダウンロードしたデータ本体：./dowqnload/data    
![image](https://github.com/user-attachments/assets/8f9b572f-86dc-41ef-9ee1-fc9149c32b15)  
