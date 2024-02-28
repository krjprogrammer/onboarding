import re
import pandas as pd
import pdfplumber
from rest_framework.response import Response
from django.core.files.uploadedfile import UploadedFile
from io import BytesIO
from pathlib import Path
import os
from PyPDF2 import PdfReader
import PyPDF2,fitz

class PDFExtractor:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.result_df = None
        self.accounts_data = None
        self.bill_date_data = None

    def extract_data(self):
        Total_Charges_list = []
        duration = []
        bill_date = []
        dates, accounts, invoices, w = [], [], [], []

        with pdfplumber.open(self.pdf_path) as pdf:
            for page_number in range(2):  
                page = pdf.pages[page_number]
                text = page.extract_text()
                lines = text.split('\n')
                match = re.search(r"https?://.*", text)
                if match:
                    url = match.group()
                    w.append(url)

                for index, line in enumerate(lines):
                    if line.startswith('InvoiceNumber AccountNumber DateDue'):
                        line = lines[index + 1]
                        items = line.split()
                        del items[3]
                        del items[4]
                        del items[3]
                        date = items[2]
                        account = items[1]
                        invoice = items[0]
                        dates.append(date)
                        accounts.append(account)
                        invoices.append(invoice)

                match = re.search(r'Total Current Charges \$([\d,]+(?:\.\d{2})?)', text)
                if match:
                    total_charges = match.group(1)
                    Total_Charges_list.append(total_charges)
                else:
                    pattern = r'Total Current Charges Due by (?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4} \$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
                    match = re.search(pattern, text)
                    if match:
                        total_charges = match.group(1)
                        Total_Charges_list.append(total_charges)

                name_regex = re.compile(r'(?:\b[A-Z][A-Z\s.-]+\b)')
                names = name_regex.findall(text)
                global name_s
                name_s = names[-1] if names else None

                address_regex = re.compile(r'\b\d+\s[A-Z0-9\s.,-]+\b\s+[A-Z]{2}\s\d{5}-\d{4}')
                addresses = address_regex.findall(text)
                global address
                address = addresses[-1] if addresses else None


                match = re.search(r'Quick Bill Summary (\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}\s*-\s*(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2}\b)', text)
                if match:
                    phone_number = match.group(1)
                    duration.append(phone_number)

                match = re.search(r'Bill Date (January|February|March|April|May|June|July|August|September|October|November|December) (\d{2}), (\d{4})', text)
                if match:
                    phone_number = match.group(1)
                    amount = match.group(2)
                    pay = match.group(3)
                    bill_date.append({
                        "phone_number": phone_number,
                        "amount": amount,
                        "pay": pay
                    })

        bill_date1 = [f"{info['phone_number']} {info['amount']} {info['pay']}" for info in bill_date]

        df = pd.DataFrame({
            'Date_Due': dates,
            'AccountNumber': accounts,
            'InvoiceNumber': invoices,
            'Website': w,
            "Total_Current_Charges": Total_Charges_list,
            "Duration": duration,
            "Bill_Date": bill_date1
        })
        self.result_df = df
        self.accounts_data = accounts
        self.bill_date_data = dates


    def extract_specific_lines_from_pdf(self, page_number, lines_to_extract):
        try:
            lines = [line for i, line in enumerate(fitz.open(self.pdf_path)[page_number - 1].get_text("text").splitlines()) if i + 1 in lines_to_extract]
            return lines
        except Exception as e:
            print(f"Error: {e}")
            return []

    def process_pdf(self, lines_to_extract):
        clnd_add = []
        extracted_lines = self.extract_specific_lines_from_pdf(1, lines_to_extract)
        for line_number, line_text in zip(lines_to_extract, extracted_lines):
            clnd_add.append(f"{line_text}")

        clnd_add = ' '.join(clnd_add)

        self.result_df["Client_Address"] = clnd_add
        self.result_df["Remidence_Address"] = "PO BOX 16810  NETWORK,NJ 07101-6810" * len(self.result_df)
        self.result_df['Billing_Name'] = name_s
        self.result_df['Billing_Address'] = address if address else ''

    def get_result_df(self):
        return self.result_df

    def get_accounts_info(self):
        return self.accounts_data
    
    def get_bill_date(self):
        return self.bill_date_data

class First:
    def __init__(self, path):
        self.path = path
        self.Lines = []
        self.line_re = re.compile(r'\d{3}-\d{3}-\d{4}')
        self.pdf = None

    def parse_pdf(self):
        self.pdf = pdfplumber.open(self.path)
        pages = self.pdf.pages
        for page in self.pdf.pages:
            text = page.extract_text()
            self.parse_text(text)
        return self.Lines
    def parse_text(self, text):
        for line in text.split('\n'):
            if self.line_re.search(line):
                items = line.split()
                items = items[:-3]

                if len(items) >= 12:
                    target_index = self.find_target_index(items)

                    if target_index is not None and target_index < len(items):
                        del items[target_index - 1]
                        items[1] = ' '.join(items[1:target_index - 1])
                        del items[2:target_index - 1]
                        self.process_items(items)

    def find_target_index(self, items):
        for i, element in enumerate(items):
            if i > 0 and (element.startswith('$') or (element.startswith('-') and '.' in element[1:])):
                return i
        return None

    def process_items(self, items):
        self.Lines.append({
            'Wireless_number': 'NA' if items[0] == '--' else items[0],
            'User_name': 'NA' if items[1] == '--' else items[1],
            'Monthly_Charges': 'NA' if items[2] == '--' else items[2],
            'Usage_and_Purchase_Charges': 'NA' if items[3] == '--' else items[3],
            'Equipment_Charges': 'NA' if items[4] == '--' else items[4],
            'Surcharges_and_Other_Charges_and_Credits': 'NA' if items[5] == '--' else items[5],
            'Taxes_Governmental_Surcharges_and_Fees': 'NA' if items[6] == '--' else items[6],
            'Third_Party_Charges_includes_Tax': 'NA' if items[7] == '--' else items[7],
            'Total_Charges': 'NA' if items[8] == '--' else items[8],
            'Voice_Plan_Usage': 'NA' if items[9] == '--' else items[9],
            'Messaging_Usage': 'NA' if items[10] == '--' else items[10],
            'Data_Usage': 'NA' if items[11] == '--' else items[11]
        })

def save_upload_file_tmp(upload_file: UploadedFile) -> str:
    temp_filename = os.path.join("/tmp", upload_file.name) 
    with open(temp_filename, "wb") as temp_file:
        for chunk in upload_file.chunks():
            temp_file.write(chunk)
    return temp_filename

class Model1():
    def __init__(self, q,accounts):
        self.pdf_data = q
        self.accounts = accounts
        self.data_new = None
        self.list1 = []
        self.lines = []

    def dim1(self, page, top_height):
        return 0, 0, page.width, top_height

    def dim2(self, page, top_height):
        return 0, top_height, page.width * 0.35, page.height

    def dim3(self, page, top_height):
        return page.width * 0.35, top_height, page.width, page.height

    def extraction(self, page, part_dims):
        if part_dims is None:
            return None
        return page.crop(part_dims).extract_text()

class Model2(Model1):
    def __init__(self, q,accounts):
        super().__init__(q,accounts)

    def max1(self):
        info = []
        with pdfplumber.open(self.pdf_data) as pdf:
            pages = len(pdf.pages)

        for num_page in range(pages):
            with pdfplumber.open(self.pdf_data) as pdf:
                page = pdf.pages[num_page]
                page_text = page.extract_text()
                if "Monthly_Charges" in page_text:
                    Lines = page_text.split("\n")
                    for line in Lines:
                        info.append(line)
        return info

    def max2(self, page):
        print(page)
        margin_left = page.bbox[0] + 510
        margin_top = page.bbox[1]
        margin_right = page.bbox[2]
        margin_bottom = page.bbox[3]
        page = page.crop((margin_left, margin_top, margin_right, margin_bottom))
        text = page.extract_text()
        Lines = text.split("\n")
        for line in Lines:
            match = re.search(
                r'(?:.*?(\$?\d+(?:\.\d+)?)|--)$',
                line)
            if match:
                self.list1.append(line)

    def max3(self):

        summary_pattern = re.compile(r'Summary for (.+?): (\d{3}-\d{3}-\d{4})')
        detail_pattern = re.compile(r'Detail for (.+?): (\d{3}-\d{3}-\d{4})')
        info1 = ''
        with pdfplumber.open(self.pdf_data) as pdf:
            no_of_pages = len(pdf.pages)

        for num_page in range(no_of_pages):
            with pdfplumber.open(self.pdf_data) as pdf:
                page = pdf.pages[num_page]
                self.max2(page)
                page_text = page.extract_text()
                summary_match = summary_pattern.search(page_text)
                detail_match = detail_pattern.search(page_text)
                if summary_match or detail_match:
                    if summary_match:
                        top_height = 0.15 * float(page.height)
                        top_part_text = self.extraction(page, self.dim1(page, top_height))
                        left_part_text = self.extraction(page, self.dim2(page, top_height))
                        right_part_text = self.extraction(page, self.dim3(page, top_height))
                        info1 = info1 + '\n' + top_part_text
                        info1 = info1 + '\n' + left_part_text
                        info1 = info1 + '\n' + right_part_text
                    else:
                        detail_line_text = [line for line in page_text.split('\n') if detail_pattern.search(line)][0]
                        top_line = page_text.split('\n').index(detail_line_text)
                        top_height = top_line * float(page.height) / len(page_text.split('\n'))
                        top_part_text = self.extraction(page, (0, 0, page.width, top_height))
                        info1 += '\n' + top_part_text
                else:
                    info1 = info1 + page_text + '\n'
        self.info1 = info1
        return info1

class Model3(Model2):
    def __init__(self, q,accounts):
        super().__init__(q,accounts)

    def data2(self):
        result = []
        current_section = None
        current_sections = None
        data = self.max3()
        lines = data.split('\n')
        check = 0
        start = 0
        list_not = ['Usage_and_Purchase_Charges', 'Voice', 'Messaging', 'Data', 'International']
        date = ""
        account = self.accounts[0]
        name = ""
        number = ""
        status = ""
        center = ""
        plan = ""
        invoice = ""
        for i, line in enumerate(lines):
            match1 = re.search(r'Bill Date (.+? \d{4})', line)
            match2 = re.search(r'Account number (\d{9}-\d{5})', line)
            match3 = re.search(r'Invoice Number (\d{10})', line)
            if match1:
                date = match1.group(1)
            if match2:
                account = match2.group(1)
            if match3:
                invoice = match3.group(1)
            if line.startswith('Account Charges (pg.2)'):
                items = line.split()
                items[1] = items[0] + ' ' + items[1]
                items[0] = '--'
                del items[2]
                result.append({
                    'Foundation Account': 'NA',
                    'Account_number': account,
                    'Group Number': 'NA',
                    'User_name': 'NA' if items[1] == '--' else items[1],
                    'Wireless_number': 'NA',
                    'User Email': 'NA',
                    'Status': 'Inactive',
                    'Cost Center': 'NA',
                    'Account Charges and Credits': 'NA' if items[2] == '--' else items[2],
                    'Plans': 'NA',
                    'Item Category': 'NA',
                    'Item Type': 'NA',
                    'Item Description': 'NA',
                    'Share Description': 'NA',
                    'Share Voice': 'NA',
                    'Share Messaging': 'NA',
                    'Share Data': 'NA',
                    'Allowance': 'NA',
                    'Used': 'NA',
                    'Billable': 'NA',
                    'Charges': ' NA' if items[9] == '--' else items[9],
                    'Order Details': 'NA',
                    'Bill Cycle Date': date,
                    'Invoice Number': invoice
                })

                break
            elif line.startswith('Account Plan and Charges** (pg.2)'):
                items = line.split()
                items[1] = items[0] + ' ' + items[1] + ' ' + items[2] + ' ' + items[3]
                items[0] = '--'
                for i in range(3):
                    del items[2]
                result.append({
                    'Foundation Account': 'NA',
                    'Account_number': account,
                    'Group Number': 'NA',
                    'User_name': 'NA' if items[1] == '--' else items[1],
                    'Wireless_number': 'NA',
                    'User Email': 'NA',
                    'Status': 'Inactive',
                    'Cost Center': 'NA',
                    'Account Charges and Credits': 'NA' if items[2] == '--' else items[2],
                    'Plans': 'NA',
                    'Item Category': 'NA',
                    'Item Type': 'NA',
                    'Item Description': 'NA',
                    'Share Description': 'NA',
                    'Share Voice': 'NA',
                    'Share Messaging': 'NA',
                    'Share Data': 'NA',
                    'Allowance': 'NA',
                    'Used': 'NA',
                    'Billable': 'NA',
                    'Charges': 'NA' if items[9] == '--' else items[9],
                    'Order Details': 'NA',
                    'Bill Cycle Date': date,
                    'Invoice Number': invoice
                })
                break
        for i, line in enumerate(lines):
            match = re.search(r'Summary for (.+?): (\d{3}-\d{3}-\d{4})', line)
            if match:
                start = 1
                name = match.group(1)
                number = match.group(2)
                center = lines[i + 1]
                if center == 'Your Plan':
                    center = 'NA'
                for item in self.lines:
                    if item.get('Wireless_number') == number and item.get('User_name') == name:
                        status = float(item.get('Monthly_Charges').replace('$', ''))
                        status = 'Active' if status > 0 else 'Inactive'
                        break
            if line.startswith('Your Plan'):
                match = re.search(r'(.*GB$|.*MB$)', lines[i + 1])
                if match:
                    plan = lines[i + 1]
                match = re.search(r'(.*GB$|.*MB$)', lines[i + 2])
                if match:
                    plan = lines[i + 2]
                else:
                    plan = lines[i + 1]
            if start != 0:
                if line.startswith('Monthly_Charges'):
                    current_section = 'Monthly_Charges'
                elif line.startswith('EquipmentCharges'):
                    current_section = 'Equipment_Charges'
                elif line.startswith('Usage_and_Purchase_Charges'):
                    current_section = 'Usage_and_Purchase_Charges'
                elif line.startswith('Surcharges') or line.startswith('Surcharges+'):
                    current_section = 'Surcharges'
                elif line.startswith('OtherChargesandCredits'):
                    current_section = 'Other Charges and Credits'
                elif line.startswith('Taxes_Governmental_Surcharges_and_Fees') or line.startswith(
                        'Taxes_Governmental_Surcharges_and_Fees+'):
                    current_section = 'Taxes_Governmental_Surcharges_and_Fees'
                elif line.startswith('Total Current Charges for'):
                    current_section = None

                match = re.search(
                    r'(.+? \d+\.\d+ .+?|.+?) (\.\d+|\d+\.\d+|\d+\,\d+\.\d+|\-\.\d+|\-\d+\.\d+|\-\d+\,\d+\.\d+)',
                    line)

                if match and (current_section not in list_not and current_section != None) and (
                        match.group(2) in self.list1 and 'Due' not in line):
                    if check == 1:
                        check = 0
                        result.append(
                            {'Foundation Account': 'NA', 'Account_number': account, 'Group Number': 'NA',
                             'User_name': name,
                             'Wireless_number': number, 'User Email': 'NA', 'Status': status, 'Cost Center': center,
                             'Account Charges and Credits': 'NA', 'Plans': plan, 'Item Category': current_section,
                             'Item Type': 'NA', 'Item Description': match.group(1), 'Share Description': 'NA',
                             'Share Voice': 'NA', 'Share Messaging': 'NA', 'Share Data': 'NA', 'Allowance': 'NA',
                             'Used': 'NA', 'Billable': 'NA',
                             'Charges': 'NA' if match.group(2) == "--" or " " else match.group(2),
                             'Order Details': 'NA', 'Bill Cycle Date': date, 'Invoice Number': invoice})
                    else:
                        result.append(
                            {'Foundation Account': 'NA', 'Account_number': account, 'Group Number': 'NA',
                             'User_name': name,
                             'Wireless_number': number, 'User Email': 'NA', 'Status': status, 'Cost Center': center,
                             'Account Charges and Credits': 'NA', 'Plans': plan, 'Item Category': current_section,
                             'Item Type': 'NA', 'Item Description': match.group(1), 'Share Description': 'NA',
                             'Share Voice': 'NA', 'Share Messaging': 'NA', 'Share Data': 'NA',
                             'Allowance': 'NA',
                             'Used': 'NA', 'Billable': 'NA',
                             'Charges': 'NA' if match.group(2) == "--" or " " else match.group(2),
                             'Order Details': 'NA', 'Bill Cycle Date': date, 'Invoice Number': invoice})

                if current_section == 'Usage_and_Purchase_Charges':
                    if re.search(r"Voice Allowance Used Billable Cost", line):
                        current_sections = 'Voice'
                    elif re.search(r"Messaging Allowance Used Billable Cost", line):
                        current_sections = 'Messaging'
                    elif re.search(r"Data Allowance Used Billable Cost", line):
                        current_sections = 'Data'
                    elif line.startswith('International Allowance Used Billable Cost'):
                        current_sections = 'International'
                    if "unlimited" not in line and ('Calling' in line) or (
                            'Gigabyte' in line and 'shared' not in lines[i + 1]) or (
                            "Shared" in line and "unlimited" not in line):
                        if "Shared" in line and "unlimited" not in line:
                            words = line.split()
                            words.insert(2, "NA")
                            line = ' '.join(words)
                        else:
                            words = line.split()
                            words.insert(3, "NA")
                            line = ' '.join(words)
                    match = re.search(
                        r'(.+?) (minutes|messages|gigabytes) (unlimited|\.\d+|\d+\.\d+|\d+\,\d+\.\d+|\-\.\d+|\-\d+\.\d+|\-\d+\,\d+\.\d+|\--) (.+) (.+) (.+)',
                        line)
                    match_I = re.search(
                        r'(International\s*Minutes)\s*(minutes|messages)\s*(\d+)\s*(\d+)\s*(-?\$\d{1,3}(?:,\d{3})*\.\d+)',
                        line)
                    if current_sections == "International" or match_I:
                        if match:
                            result.append({'Foundation Account': 'NA', 'Account_number': account, 'Group Number': 'NA',
                                           'User_name': name, 'Wireless_number': number, 'User Email': 'NA',
                                           'Status': status, 'Cost Center': center, 'Account Charges and Credits': 'NA',
                                           'Plans': plan, 'Item Category': current_sections,
                                           'Item Type': match.group(2),
                                           'Item Description': match.group(1), 'Share Description': 'NA',
                                           'Share Voice': 'NA', 'Share Messaging': 'NA', 'Share Data': 'NA',
                                           'Allowance': match.group(3),
                                           'Used': match.group(4), 'Billable': match.group(5),
                                           'Charges': 'NA' if match.group(6) == "--" or " " else match.group(6),
                                           'Order Details': 'NA', 'Bill Cycle Date': date, 'Invoice Number': invoice})
                        if match_I:
                            result.append(
                                {'Foundation Account': 'NA', 'Account_number': account, 'Group Number': 'NA',
                                 'User_name': name, 'Wireless_number': number, 'User Email': 'NA', 'Status': status,
                                 'Cost Center': center, 'Account Charges and Credits': 'NA', 'Plans': plan,
                                 'Item Category': current_sections, 'Item Type': match_I.group(2),
                                 'Item Description': match_I.group(1), 'Share Description': 'NA',
                                 'Share Voice': 'NA', 'Share Messaging': 'NA', 'Share Data': 'NA',
                                 'Allowance': match_I.group(3),
                                 'Used': match_I.group(4), 'Billable': match_I.group(5),
                                 'Charges': 'NA' if match_I.group(5) == "--" or " " else match_I.group(5),
                                 'Order Details': 'NA', 'Bill Cycle Date': date, 'Invoice Number': invoice})
                    else:
                        if match:
                            result.append({'Foundation Account': 'NA', 'Account_number': account, 'Group Number': 'NA',
                                           'User_name': name, 'Wireless_number': number, 'User Email': 'NA',
                                           'Status': status, 'Cost Center': center, 'Account Charges and Credits': 'NA',
                                           'Plans': plan, 'Item Category': current_sections,
                                           'Item Type': match.group(2),
                                           'Item Description': match.group(1), 'Share Description': 'NA',
                                           'Share Voice': 'NA', 'Share Messaging': 'NA', 'Share Data': 'NA',
                                           'Allowance': match.group(3),
                                           'Used': match.group(4), 'Billable': match.group(5),
                                           'Charges': 'NA' if match.group(6) == "--" or " " else match.group(6),
                                           'Order Details': 'NA', 'Bill Cycle Date': date, 'Invoice Number': invoice})
        self.result = result
        return result

class Model4(First, Model3):
    def __init__(self, q,accounts):
        super().__init__(q)
        self.pdf_data = q
        self.accounts = accounts
        self.list1 = []

    def process_pdf(self):
        lines = self.parse_pdf()
        self.lines = lines
        data_from_model3 = self.data2()
        df_lines = pd.DataFrame(lines)
        df_model3 = pd.DataFrame(data_from_model3)
        merged_df = pd.merge(df_lines, df_model3[['Wireless_number', 'Account_number', 'Plans']], left_on='Wireless_number', right_on='Wireless_number', how='left')
        merged_df = merged_df.drop_duplicates(subset='Wireless_number')
        merged_df = merged_df.reset_index(drop=True)
        return merged_df
