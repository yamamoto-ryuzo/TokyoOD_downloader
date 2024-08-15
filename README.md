# TokyoOD_downloader  
## 開発主旨  
[東京都オープンデータカタログサイト](https://portal.data.metro.tokyo.lg.jp/)からオープンデータ一覧をダウンロードして、CSVデータのうち位置情報のあるデータを抽出し、ダウンロードしたデータは以下でPostgRESTとして公開予定。（サーバーの能力の問題から東京都、目黒区のみです。）  
　https://github.com/yamamoto-ryuzo/PostgREST-installation-Japanese-memo/blob/main/使用方法.md  

## 仕様  
　・Pythonを設置したフォルダ以下へのアクセス権および作業領域・データ保持が可能であること    
　・EPSGコード不明はいったんEPSG：****で処理   
　・位置情報属性は緯度・経度に統一  
　・文字コードは　UTF-8　に統一   
