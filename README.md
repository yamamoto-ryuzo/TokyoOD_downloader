# TokyoOD_downloader  
## 開発主旨  
[東京都オープンデータカタログサイト](https://portal.data.metro.tokyo.lg.jp/)からオープンデータ一覧をダウンロードして、CSVデータのうち位置情報のあるデータを抽出し、ダウンロードしたデータは以下でPostgRESTとして公開予定。（サーバーの能力の問題から東京都、目黒区のみです。）  
　https://github.com/yamamoto-ryuzo/PostgREST-installation-Japanese-memo/blob/main/使用方法.md  

## 仕様  
　・Pythonを設置したフォルダ以下へのアクセス権および作業領域・データ保持が可能であること    
　・EPSGコード不明はいったんEPSG：****で処理   
　・位置情報属性は緯度・経度に統一  
　・文字コードは　UTF-8　に統一   

## オープンデータ一のをダウンロード方法  
データ一覧については下記の手順でCSVとして取得可能です。  
①[東京都オープンデータカタログサイト](https://portal.data.metro.tokyo.lg.jp/)のトップページにて左上にある「一覧からデータを探す」をクリックする。  
②データセット一覧の画面に切り替わると「xxxx件のデータセットが見つかりました」のメッセージが表示される。  
③ ②の画面にて「検索結果を出力」ボタン（検索キーワード入力用のテキストボックス上方に配置されている）をクリック  
するとメッセージの対象となった件数に該当するデータ一覧をCSVとして取得可能  
　今回はこんな感じを前提で「 https://catalog.data.metro.tokyo.lg.jp/dataset?q=目黒区res_format=CSV   」  
  一覧が自動取得できない構造なのが残念。  
