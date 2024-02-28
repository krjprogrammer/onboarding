import sqlite3
import json
from pathlib import Path
import time
import pandas as pd
from io import BytesIO
from scripts.verizon import PDFExtractor,First,Model1,Model2,Model3,Model4



def extract_data_from_pdf(pdf_path,company_nm,vendor_nm):
    lines_to_extract = [2, 3, 4, 5]
    extractor = PDFExtractor(pdf_path)
    extractor.extract_data()
    extractor.process_pdf(lines_to_extract)
    data = extractor.get_result_df()
    acc_info = extractor.get_accounts_info()
    bill_date_info = extractor.get_bill_date()
    data_dict = data.to_dict(orient='records')
    for entry in data_dict:
        entry['company'] = company_nm
        entry['vendor'] = vendor_nm
    return data_dict,acc_info,bill_date_info

def extract_total_pdf_data(pdf_path,acc_info):
    extractor = Model4(pdf_path,acc_info)
    result = extractor.process_pdf()
    res_data_dict = result.to_dict(orient='records')
    return res_data_dict

def save_to_pdf_data_table(data):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    for item in data:
        keys = ', '.join(item.keys())
        values = ', '.join([f'"{value}"' for value in item.values()])
        cursor.execute(f"INSERT INTO tech_pdf_data_table ({keys}) VALUES ({values})")

    conn.commit()
    conn.close()

def process_csv_data(csv_path):
    df_csv = pd.read_csv(csv_path)
    df_csv.columns = df_csv.columns.str.strip()
    df_csv.columns = df_csv.columns.str.strip().str.replace('-', '').str.replace(r'\s+', ' ', regex=True).str.replace(' ', '_')

    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    def fetch_latest_entry():
        cursor.execute("SELECT * FROM tech_mappingdata ORDER BY id DESC LIMIT 1")
        latest_entry = cursor.fetchone()
        return latest_entry

    def is_wireless_number_done(entry_dict):
        return entry_dict.get('Wireless_number') == 'Done'

    while True:
        latest_entry = fetch_latest_entry()
        column_names = [description[0] for description in cursor.description]
        latest_entry_dict = {column_names[i]: latest_entry[i] for i in range(len(column_names))}
        del latest_entry_dict['id']
        if is_wireless_number_done(latest_entry_dict):
            time.sleep(2)
        else:
            column_mapping = {v: k for k, v in latest_entry_dict.items()}
            filtered_mapping = {key: value for key, value in column_mapping.items() if key != 'NA'}
            missing_columns = [col for col in filtered_mapping.keys() if col not in df_csv.columns]
            for key, value in latest_entry_dict.items():
                if value == "NA":
                    latest_entry_dict[key] = key
            columns_to_keep = [col for col in latest_entry_dict.values() if col in df_csv.columns]
            df_csv = df_csv[columns_to_keep]
            df_csv.rename(columns=filtered_mapping, inplace=True)
            latest_entry_dict['Wireless_number'] = 'Done'
            update_query = "UPDATE tech_mappingdata SET " + ", ".join(f"{key} = '{value}'" for key, value in latest_entry_dict.items()) + f" WHERE id = {latest_entry[0]}"
            cursor.execute(update_query)
            conn.commit()
            break

    cursor.execute("SELECT DISTINCT Account_number FROM tech_pdf_data_table")
    unique_account_numbers = cursor.fetchall()
    unique_account_numbers_list = [acc[0] for acc in unique_account_numbers]
    df_acc = df_csv['Account_number'].iloc[0]
    checked_acc = df_acc if df_acc in unique_account_numbers_list else None

    if checked_acc:
        cursor.execute("SELECT * FROM tech_pdf_data_table WHERE Account_number=?", (checked_acc,))
        data_related_to_account = cursor.fetchall()
        column_names_pdf = [description[0] for description in cursor.description]
        data_df_csv = pd.DataFrame(data_related_to_account,columns=column_names_pdf)
        merged_df = pd.merge(data_df_csv, df_csv, left_on='Wireless_number', right_on='Wireless_number', how='left')
        merged_df.drop_duplicates(subset='Wireless_number', inplace=True)
        merged_df.reset_index(drop=True, inplace=True)
        cursor.execute("SELECT * FROM tech_base_data_table WHERE AccountNumber=?", (merged_df['Account_number_x'].iloc[0],))
        base_data_entry = cursor.fetchone()
        company_name = base_data_entry[12] 
        vendor_name = base_data_entry[13]

        merged_data = merged_df.to_dict(orient='records')
        for entry in merged_data:
            entry['company'] = company_name
            entry['vendor'] = vendor_name

        for item in merged_data:
            keys = ', '.join(item.keys())
            values = ', '.join([f'"{value}"' for value in item.values()])
            cursor.execute(f"INSERT INTO tech_merged_table ({keys}) VALUES ({values})")

        conn.commit()
        conn.close()

def save_to_base_data_table(data):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    for item in data:
        keys = ', '.join(item.keys())
        values = ', '.join([f'"{value}"' for value in item.values()])
        cursor.execute(f"INSERT INTO tech_base_data_table ({keys}) VALUES ({values})")

    conn.commit()
    conn.close()


def save_user_pdf(acc_no,bill_date,pdf_path):
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    sql_query = """
    INSERT INTO tech_user_pdf (acc_no, bill_date, pdf)
    VALUES (?, ?, ?)
"""
    cursor.execute(sql_query, (acc_no,bill_date,pdf_path))
    conn.commit()
    cursor.close()
    conn.close()


def process_pdf_from_buffer():
    buffer_path = Path('buffer.json')
    if buffer_path.exists():
        with open(buffer_path, 'r') as file:
            buffer_data_content = file.read()
            print("Buffer Data Content:",buffer_data_content)
            try:
                buffer_data = json.loads(buffer_data_content)
            except json.JSONDecodeError as e:
                print("Error decoding JSON:", e)
                return
    else:
        buffer_data = []

    for data_entry in buffer_data:
        pdf_path = data_entry.get('pdf_path')
        company_name = data_entry.get('company_name')
        vendor_name = data_entry.get('vendor_name')
        data,acc_info,bill_date_info = extract_data_from_pdf(pdf_path,company_name,vendor_name)
        save_user_pdf(acc_info[0],bill_date_info[0],pdf_path)
        save_to_base_data_table(data)
        pdf_data = extract_total_pdf_data(pdf_path,acc_info)
        save_to_pdf_data_table(pdf_data)
 

    if buffer_path.exists():
        buffer_path.unlink()


def process_csv_from_buffer():
    buffer_path = Path('buffer_csv.json')
    if buffer_path.exists():
        with open(buffer_path, 'r') as file:
            buffer_data_content = file.read()
            print("Buffer Data Content:",buffer_data_content)
            try:
                buffer_data = json.loads(buffer_data_content)
            except json.JSONDecodeError as e:
                print("Error decoding JSON:", e)
                return
    else:
        buffer_data = []

    for data_entry in buffer_data:
        csv_path = data_entry.get('csv_path')
        process_csv_data(csv_path)

 

    if buffer_path.exists():
        buffer_path.unlink()

while True:
    process_pdf_from_buffer()
    process_csv_from_buffer()
    time.sleep(1)