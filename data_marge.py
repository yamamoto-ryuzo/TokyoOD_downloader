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