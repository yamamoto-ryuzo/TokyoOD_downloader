import os
import chardet
import pandas as pd
import numpy as np

def process_csv_files(input_directory, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    if not os.path.exists(input_directory):
        os.makedirs(input_directory)

    for filename in os.listdir(input_directory):
        if filename.endswith('.csv'):
            input_path = os.path.join(input_directory, filename)
            output_path = os.path.join(output_directory, filename)
            process_single_file(input_path, output_path)

def process_single_file(input_path, output_path):
    print(f"Processing file: {input_path}")

    ## エンコードの確認
    with open(input_path, 'rb') as f:
        content = f.read()
        result = chardet.detect(content)
        print(f"Detected Encoding: {result['encoding']}, Confidence: {result['confidence']}")

    ## エンコーディングの検証
    encoding = result['encoding']
    common_encodings = ['utf-8', 'shift_jis', 'euc-jp', 'iso-2022-jp', 'cp932']
    if encoding is None or encoding == 'NON' or result['confidence'] < 0.7:
        print(f"{input_path}のエンコーディングを再検証します。")
        for enc in common_encodings:
            try:
                with open(input_path, 'r', encoding=enc) as f:
                    text = f.read()
                encoding = enc
                print(f"エンコーディングを{enc}と判定しました。")
                break
            except UnicodeDecodeError:
                continue
        else:
            print(f"{input_path}のエンコーディングを判定できませんでした。")
            return

    ## エンコーディングの変換とファイルの保存
    try:
        # ヘッダーなしで読み込む
        df = pd.read_csv(input_path, encoding=encoding, on_bad_lines='skip', header=None)
        
        ## 先頭行のデータ存在率を確認し、必要に応じて不要な行を削除
        threshold = 0.5  # 50%のしきい値
        valid_start_index = find_valid_start_row(df, threshold)
        if valid_start_index > 0:
            df = df.iloc[valid_start_index:].reset_index(drop=True)
            print(f"{valid_start_index}行の不要な行を削除しました。")
        
        ## 空の行を削除
        df = df.dropna(how='all')
        
        ## CSVファイルを保存
        df.to_csv(output_path, index=False, header=False, encoding='utf-8')
        print(f"{input_path}をUTF-8に変換し、空の行を削除して{output_path}に保存しました。")
    except Exception as e:
        print(f"{input_path}の変換中にエラーが発生しました: {str(e)}")
        return

    ## 属性：名称に類似属性のデータを統一
    load_and_modify_csv(os.path.dirname(output_path), os.path.basename(output_path))

    ## 緯度列の確認とファイル名変更
    try:
        data = pd.read_csv(output_path, encoding='UTF-8', header=None)
        check_columns = ['緯度', '"緯度"', 'latitude', 'lat', 'x']
        if any(col.lower() in data.iloc[0].astype(str).str.lower().values for col in check_columns):
            new_file_name = f"GIS_{os.path.basename(output_path)}"
            print(f"{output_path}: 位置情報があります。")
        else:
            new_file_name = f"NON_{os.path.basename(output_path)}"
            print(f"{output_path}: 位置情報がありません。")
        new_output_path = os.path.join(os.path.dirname(output_path), new_file_name)
        force_rename(output_path, new_output_path)
        print(f"ファイル名を変更しました: {output_path} -> {new_output_path}")
    except Exception as e:
        print(f"{output_path}の処理中にエラーが発生しました: {str(e)}")

def find_valid_start_row(df, threshold):
    for i in range(len(df)):
        if df.iloc[i].notna().mean() >= threshold:
            return i
    return 0  # 有効な行が見つからない場合は0を返す

def load_and_modify_csv(directory, filename):
    # この関数の実装は省略されています。必要に応じて実装してください。
    pass

def force_rename(old_path, new_path):
    if os.path.exists(new_path):
        os.remove(new_path)
    os.rename(old_path, new_path)

# 使用例
#if __name__ == "__main__":
#    input_directory = './data/csv'
#    output_directory = './data/csv_convert'
#    process_csv_files(input_directory, output_directory)