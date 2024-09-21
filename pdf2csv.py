# pip install PyPDF2 pdfplumber pandas openpyxl

import os
import pdfplumber
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def is_valid_table(table):
    if not table or len(table) < 2 or len(table[0]) < 2:
        return False
    
    # すべての行が同じ列数を持つことを確認
    if not all(len(row) == len(table[0]) for row in table):
        return False
    
    # データの少なくとも80%が非空であることを確認
    data_array = np.array(table)
    non_empty_ratio = np.count_nonzero(data_array != '') / data_array.size
    return non_empty_ratio >= 0.8

def has_latitude(table):
    header = table[0]
    lat_keywords = ['lat', '緯度', 'latitude']
    return any(any(keyword in col.lower() for keyword in lat_keywords) for col in header)

def extract_tables_from_pdf(pdf_path):
    valid_tables = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    if is_valid_table(table):
                        df = pd.DataFrame(table[1:], columns=table[0])
                        valid_tables.append((df, has_latitude(table)))
    except Exception as e:
        logging.error(f"{pdf_path} の処理中にエラーが発生しました: {str(e)}")
    return valid_tables

def save_table_to_csv(table, output_path, has_latitude):
    try:
        base_name = os.path.basename(output_path)
        dir_name = os.path.dirname(output_path)
        if has_latitude:
            new_name = f"GIS_{base_name}"
        else:
            new_name = base_name
        new_path = os.path.join(dir_name, new_name)
        
        table.to_csv(new_path, index=False, encoding='utf-8-sig')
        logging.info(f"表をCSVファイルに保存しました: {new_path}")
    except Exception as e:
        logging.error(f"{new_path} の保存中に問題が発生しました: {str(e)}")

def process_pdf(input_path, output_folder):
    try:
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        
        logging.info(f"処理中: {input_path}")
        
        tables = extract_tables_from_pdf(input_path)
        
        if not tables:
            logging.warning(f"{input_path} に有効な表が見つかりませんでした。")
            return f"警告: {input_path} - 有効な表なし"
        
        for i, (table, has_latitude) in enumerate(tables, 1):
            output_path = os.path.join(output_folder, f"{base_name}_table_{i}.csv")
            save_table_to_csv(table, output_path, has_latitude)
        
        return f"成功: {input_path} - {len(tables)}個の表を保存"
    except Exception as e:
        return f"エラー: {input_path} - {str(e)}"

def process_pdfs_in_batches(input_folder, output_folder, batch_size=5):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    pdf_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.lower().endswith('.pdf')]
    
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        for i in range(0, len(pdf_files), batch_size):
            batch = pdf_files[i:i+batch_size]
            futures = {executor.submit(process_pdf, pdf_file, output_folder): pdf_file for pdf_file in batch}
            for future in as_completed(futures):
                pdf_file = futures[future]
                try:
                    result = future.result()
                    logging.info(result)
                except Exception as e:
                    logging.error(f"{pdf_file} の処理中にエラーが発生しました: {str(e)}")

    logging.info("すべてのPDFファイルの処理が完了しました")

# メイン処理
if __name__ == "__main__":
    input_folder = "./download/data"
    output_folder = "./download/output"
    process_pdfs_in_batches(input_folder, output_folder)