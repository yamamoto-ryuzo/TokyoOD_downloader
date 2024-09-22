# pip install xlrd>=2.0.1 pandas openpyxl
import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

import pandas as pd
import os
import logging

def convert_excel_to_csv(input_path: str, output_folder: str) -> str:
    try:
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        logging.info(f"処理中: {input_path}")
        
        xls = pd.ExcelFile(input_path)
        
        processed_sheets = 0
        for sheet_name in xls.sheet_names:
            print(f"シート名: {sheet_name}")
            
            # 出力フォルダが存在しない場合は作成
            os.makedirs(output_folder, exist_ok=True)

            output_path = os.path.join(output_folder, f"{base_name}_{sheet_name}.csv")

            # シートの全データを読み込む
            df = pd.read_excel(xls, sheet_name)
            
            # Unnamed列を空白に置換
            df.columns = df.columns.str.replace('^Unnamed: \d+$', '', regex=True)
            
            # インデックスを付けずにCSVとして保存
            df.to_csv(output_path, index=False, encoding='utf-8')
            logging.info(f"シートをCSVファイルに保存しました: {output_path}")
            processed_sheets += 1

        return f"成功: {input_path} - {processed_sheets}個のシートを保存"
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

#if __name__ == "__main__":
#    input_folder = "./data/xls"
#    output_folder = "./data/csv"
#    process_excels_in_batches(input_folder, output_folder)