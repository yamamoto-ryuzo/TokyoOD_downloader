# TokyoOD_downloader
## 最終目標  
[東京都オープンデータカタログサイト](https://portal.data.metro.tokyo.lg.jp/)からオープンデータ一覧をダウンロードして、CSVデータのうち位置情報のあるデータを抽出し、ダウンロードしたデータは以下でPostgRESTとして公開予定。（サーバーの能力の問題から東京都、目黒区のみです。）  
　https://github.com/yamamoto-ryuzo/PostgREST-installation-Japanese-memo/blob/main/使用方法.md  

## 仕様
　・対応ファイル形式  
 　　　CSV  
　・文字コードは　UTF-8　に統一   
　・CSVデータをダウンロードした場合、座標値を含むものとそうでないものも仕分け  
　　　　　座標値あり：GIS_元のファイル名  
　　　　　座標値なし：NON_元のファイル名  

## 利用方法
以下を同じフォルダに設置してください。  
　　本体：TokyoOD_downloder.exe  
　　設定ファイル：config.txt  
  　　　
作成されるフォルダ  
　　ダウンロードする予定のURL一覧：./download/dataURLList.csv  
　　ダウンロードしたデータ本体：./dowqnload/data  
## 出力サンプル
ダウンロードする予定のURL一覧：./download/dataURLList.csv

ダウンロードしたデータ本体：./dowqnload/data  
