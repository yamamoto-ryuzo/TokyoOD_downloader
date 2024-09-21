# pip install xlrd>=2.0.1 pandas openpyxl
import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

import os
import logging
import pandas as pd

import os
import logging
import pandas as pd

def convert_excel_to_csv(input_path: str, output_folder: str) -> str:
    def detect_and_read_multiline_header(sheet_name):
        max_header_rows = 5  # 最大ヘッダー行数
        xls = pd.ExcelFile(input_path)

        for n in range(1, max_header_rows + 1):
            try:
                df = pd.read_excel(xls, sheet_name, header=list(range(n)), nrows=5)
                if not df.empty and not df.columns.isnull().all():
                    return df, n
            except Exception:
                continue
        return None, 0

    try:
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        logging.info(f"処理中: {input_path}")
        
        xls = pd.ExcelFile(input_path)
        
        processed_sheets = 0
        for sheet_name in xls.sheet_names:
            print(f"シート名: {sheet_name}")
            
            df, header_rows = detect_and_read_multiline_header(sheet_name)
            
            if df is not None:
                print(f"ヘッダー情報 ({header_rows}行):")
                print(df.columns.tolist())

                # '緯度'列の有無をチェック
                has_latitude = '緯度' in df.columns

                # 無名列の有無をチェック
                unnamed_columns = df.columns.str.contains('^Unnamed:', na=False)

                # プレフィックスの決定
                if has_latitude:
                    prefix = 'GIS_'
                elif not any(unnamed_columns):
                    prefix = 'NON_'
                else:
                    prefix = 'ERR_'

                # 出力フォルダが存在しない場合は作成
                os.makedirs(output_folder, exist_ok=True)

                output_path = os.path.join(output_folder, f"{prefix}{base_name}_{sheet_name}.csv")

                # 全データを読み込む（検出されたヘッダー行数を使用）
                df_full = pd.read_excel(xls, sheet_name, header=list(range(header_rows)))
                df_full.to_csv(output_path, index=False, encoding='utf-8')
                logging.info(f"シートをCSVファイルに保存しました: {output_path}")
                processed_sheets += 1
            else:
                logging.warning(f"シート '{sheet_name}' にはヘッダーがないためスキップしました")

        return f"成功: {input_path} - {processed_sheets}個のシートを保存（ヘッダーのないシートはスキップ）"
    except Exception as e:
        logging.error(f"エラー発生: {input_path} - {str(e)}")
        return f"エラー: {input_path} - {str(e)}"
import pandas as pd
import os

def process_excels_in_batches(input_folder, output_folder, batch_size=5):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    excel_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.lower().endswith(('.xlsx', '.xls'))]
    
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        for i in range(0, len(excel_files), batch_size):
            batch = excel_files[i:i+batch_size]
            futures = {executor.submit(convert_excel_to_csv, excel_file, output_folder): excel_file for excel_file in batch}
            for future in as_completed(futures):
                excel_file = futures[future]
                try:
                    result = future.result()
                    logging.info(result)
                except Exception as e:
                    logging.error(f"{excel_file} の処理中にエラーが発生しました: {str(e)}")

    logging.info("すべてのExcelファイルの処理が完了しました")

if __name__ == "__main__":
    input_folder = "./download/data"
    output_folder = "./download/output"
    process_excels_in_batches(input_folder, output_folder)