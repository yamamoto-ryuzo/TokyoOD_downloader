# モジュールのインストール
# pip install chardet pandas

import os
import chardet
import pandas as pd
import shutil

def process_csv_files(input_directory, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

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

    ## エンコーディングの変換とファイルの保存
    try:
        with open(input_path, 'r', encoding=encoding) as f:
            text = f.read()
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"{input_path}をUTF-8に変換し、{output_path}に保存しました。")
    except Exception as e:
        print(f"{input_path}の変換中にエラーが発生しました: {str(e)}")
        return  # エラーが発生した場合、この関数を終了

    ## 属性：名称に類似属性のデータを統一
    load_and_modify_csv(os.path.dirname(output_path), os.path.basename(output_path))

    ## 緯度列の確認とファイル名変更
    try:
        data = pd.read_csv(output_path, encoding='UTF-8', on_bad_lines='skip')
        check_columns = ['緯度', '"緯度"', 'latitude', 'lat', 'x']
        if any(col in data.columns for col in check_columns):
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

def load_and_modify_csv(directory, filename):
    # この関数の実装は省略されています。必要に応じて実装してください。
    pass

def force_rename(old_path, new_path):
    if os.path.exists(new_path):
        os.remove(new_path)
    os.rename(old_path, new_path)

# 使用例
input_directory = './data/csv'
output_directory = './data/output'
process_csv_files(input_directory, output_directory)
