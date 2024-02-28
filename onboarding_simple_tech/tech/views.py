from django.shortcuts import render
from django.core.serializers import serialize
from django.urls import reverse
from django.http import JsonResponse,FileResponse,HttpResponse
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
import tempfile,time
from rest_framework.response import Response
from io import BytesIO
from pathlib import Path
import os,json
import pdfplumber
from django.forms.models import model_to_dict
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import api_view
from .models import base_data_table,pdf_data_table,merged_table,Company,MappingData,Vendor_data_table,Column_mapping_data,Portal_information_data,user_pdf,contract_table
from .serializers import bill_data_serializer,base_data_serializer,mapping_serializer,column_serializer,portal_info_serializer
from .serializers import company_serializer,vendor_data_serializer
from rest_framework import status
from .models import Company


@api_view(['POST'])
def upload_file(request):
        uploaded_file= request.FILES.get('file')
        company_name = request.POST.get('company_name')
        vendor_name = request.POST.get('vendor_name')
        accounts = []
        dates = []
        with pdfplumber.open(uploaded_file) as pdf:
            for page_number in range(2):  
                page = pdf.pages[page_number]
                text = page.extract_text()
                lines = text.split('\n')
                for index, line in enumerate(lines):
                    if line.startswith('InvoiceNumber AccountNumber DateDue'):
                        line = lines[index + 1]
                        items = line.split()
                        del items[3]
                        del items[4]
                        del items[3]
                        date = items[2]
                        account = items[1]
                        dates.append(date)
                        accounts.append(account)
        acc_no = accounts[0]
        bill_date = dates[0]
        print(acc_no,bill_date)
        acc_exists = base_data_table.objects.filter(AccountNumber=acc_no)
        bill_date_exists = base_data_table.objects.filter(Date_Due=bill_date)
        if acc_exists:
            if bill_date_exists:
                return Response('Bill already exists,upload another one')
            
        storage = FileSystemStorage(location='uploads/')
        filename = storage.save(uploaded_file.name, uploaded_file)
        path = storage.path(filename)

        buffer_data = {'pdf_path': path,'company_name': company_name, 'vendor_name': vendor_name}
        buffer_path = Path('buffer.json')
        with open(buffer_path, 'w') as file:
            json.dump([buffer_data], file)
            return Response({'status': 'success', 'message': 'File uploaded successfully.'}, status=200)

@api_view(['POST'])
def upload_csv(request):
    file = request.FILES.get('file')
    try:
        df_csv = pd.read_csv(BytesIO(file.read()))
        df_csv.columns = df_csv.columns.str.strip()
        df_csv.columns = df_csv.columns.str.strip().str.replace('-', '').str.replace(r'\s+', ' ', regex=True).str.replace(' ', '_')
        columns_list = df_csv.columns.tolist()
        column_names_str = ','.join(columns_list)
        col_dict = {
            'columns':column_names_str
        }
        instance = Column_mapping_data(**col_dict)
        instance.save()
        with tempfile.NamedTemporaryFile(delete=False) as temper_file:
            for chunk in file.chunks():
                temper_file.write(chunk)
            path = temper_file.name

        buffer_data_csv = {'csv_path': path}
        buffer_path_csv = Path('buffer_csv.json')
        with open(buffer_path_csv, 'w') as file:
            json.dump([buffer_data_csv], file)
            return Response({'status': 'success', 'message': 'CSV uploaded successfully.'}, status=200)

    except Exception as e:
        return Response({'status': 'error', 'message': str(e)})

@api_view(['POST'])
def upload_contract(request):
    contract = request.FILES.get('file')
    name_of_file = request.POST.get('filename')
    storage = FileSystemStorage(location='uploaded_contracts/')
    filename = storage.save(contract.name, contract)
    path = storage.path(filename)
    instance = contract_table(contract_filename=name_of_file,contract_pdf_path=path)
    instance.save()
    
class get_column_names(APIView):
    def get(self,request):
        db_data = Column_mapping_data.objects.all()
        serializer = column_serializer(db_data,many=True)
        return Response(serializer.data)

class bill_data_api(APIView):
    def get(self,request):
        db_data = merged_table.objects.all()
        serializer = bill_data_serializer(db_data,many=True)
        return Response(serializer.data)
    
class current_bill_data(APIView):
    def get(self,request,acc_no):
        db_data = merged_table.objects.filter(Account_number_y=acc_no)
        serializer = bill_data_serializer(db_data, many=True)
        return Response(serializer.data)
    
class specific_company_data(APIView):
    def get(self,request,param):
        db_data = Company.objects.filter(name=param)
        serializer = company_serializer(db_data,many=True)
        return Response(serializer.data)

class current_base_data_api(APIView):
    def get(self,request):
        latest_upload = base_data_table.objects.latest('id')
        account_number = latest_upload.AccountNumber
        db_data = base_data_table.objects.filter(AccountNumber=account_number)
        serializer = base_data_serializer(db_data,many=True)
        return Response(serializer.data)

class total_base_data(APIView):
    def get(self,request):
        db_data = base_data_table.objects.all()
        serializer = base_data_serializer(db_data,many=True)
        return Response(serializer.data)

class post_company_data(APIView):
    def post(self,request):
       data = request.data
       serializer = company_serializer(data=data)
       if serializer.is_valid():
           serializer.save()
           return Response(serializer.data)
       return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class comapany_api_view(APIView):
    def get(self,request):
        db_data = Company.objects.all()
        serializer = company_serializer(db_data,many=True)
        return Response(serializer.data)
    
class post_mapping_data(APIView):
    def post(self,request):
        data = request.data
        serializer = mapping_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class get_mapping_data(APIView):
    def get(self,request):
        db_data = MappingData.objects.all()
        serializer = mapping_serializer(db_data, many=True)
        return Response(serializer.data)
  
class vendor_data(APIView):
    def get(self,request):
        db_data = Vendor_data_table.objects.all()
        serializer = vendor_data_serializer(db_data,many=True)
        return Response(serializer.data)
    
class post_portal_info(APIView):
    def post(self,request):
        data = request.data
        serializer = portal_info_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.error,status=status.HTTP_400_BAD_REQUEST)
    
class get_portal_info(APIView):
    def get(self,request):
        db_data = Portal_information_data.objects.all()
        serializer = portal_info_serializer(db_data,many=True)
        return Response(serializer.data)
    
class post_edited_data(APIView):
    def post(self, request):
        data = json.loads(request.body)
        account_number = data.get('Account_number')
        try:
            base_data_obj = base_data_table.objects.get(AccountNumber=account_number)
            fields_to_update = {
                'vendor': 'vendor',
                'Bill_Date': 'Bill_Date',
                'contact_number': 'contact_number',
                'Current_charges': 'Total_Current_Charges',
                'Billing_Cycle': 'Duration',
                'Payment_Type':'Payment_Type',
                'Address': 'Client_Address',
                'Invoice_Method': 'Invoice_Method'
            }
            for edit_field, base_field in fields_to_update.items():
                if data.get(edit_field) != 'NA':
                    setattr(base_data_obj, base_field, data.get(edit_field))
            base_data_obj.save()
            return Response({'status': 'success', 'message': 'Data updated successfully'})
        except base_data_table.DoesNotExist:
            return Response({'status': 'error', 'message': 'Account number does not exist'})
        
class delete_ban(APIView):
    def post(self,request):
        data = request.data
        account_number = data.get('Account_number')
        delete_base_acc_no = base_data_table.objects.filter(AccountNumber=account_number)
        delete_merged_acc_no = merged_table.objects.filter(Account_number_y=account_number)
        delete_base_acc_no.delete()
        delete_merged_acc_no.delete()
        return Response("BAN deleted sucessfully")

class view_bills(APIView):
    def post(self,request):
        data = request.data
        vendor = data.get('Vendor')
        acc_no = data.get('BAN')
        related_bill_data = base_data_table.objects.filter(AccountNumber=acc_no,vendor=vendor)
        json_data = serialize('json',related_bill_data)
        return Response({'bill_data': json_data})

class view_attachment(APIView):
    def post(self,request):
        data = request.data
        acc_no = data.get('acc_no')
        bill_date = data.get('bill_date')
        try:
            pdf = user_pdf.objects.get(acc_no=acc_no, bill_date=bill_date)
            pdf_path = pdf.pdf.path
            if os.path.exists(pdf_path):
                with open(pdf_path, 'rb') as f:
                    response = HttpResponse(f.read(), content_type='application/pdf')
                    response['Content-Disposition'] = 'inline; filename="attachment.pdf"'
                    return response
            else:
                return HttpResponse("Attachment not found first", status=404)
        except ObjectDoesNotExist:
            return HttpResponse("Attachment not found second", status=404)
        
class view_contract_attachment(APIView):
    def post(self,request):
        data = request.data
        filename = data.get('filename')
        try:
            contract = contract_table.objects.get(contract_filename=filename)
            contract_path = contract.contract_pdf_path.path
            if os.path.exists(contract_path):
                with open(contract_path,'rb') as f:
                    response = HttpResponse(f.read(), content_type='application/pdf')
                    response['Content-Disposition'] = 'inline; filename="attachment.pdf"'
                    return response
            else:
                return HttpResponse("Attachment not found first", status=404)
        except ObjectDoesNotExist:
            return HttpResponse("Attachment not found second", status=404)
    

class add_more_lines(APIView):
    def post(self,request):
        data = request.data
        wirelees_number = data.get('Wireless_number','NA')
        user_name = data.get('User_Name','NA')
        plan_type = data.get('Plan_Type','NA')
        ban = data.get('Account_Number','NA')
        device_id = data.get('Device_ID','NA')
        sim = data.get('Mobie_SIM_Num','NA')
        cost_center = data.get('Cost_Center','NA')
        total_charges = data.get('Total_charges','NA')
        Third_Party_Charges_includes_Tax = data.get('Thrid_party_charges','NA')
        Monthly_chrages = data.get('Monthly_charges','NA')

        instance = merged_table(wirelees_number=wirelees_number,User_name_y=user_name,Plans=plan_type,Account_number=ban,Current_device_ID_4G_only=device_id,SIM=sim,Cost_center=cost_center,Total_Charges=total_charges,Third_Party_Charges_includes_Tax=Third_Party_Charges_includes_Tax,Monthly_Charges=Monthly_chrages)
        instance.save()

class bill_details(APIView):
    def post(self,request):
        data = request.data
        acc_no = data.get('Account_number')
        bill_details = merged_table.objects.filter(Account_number_y=acc_no)
        bill_details_json = serialize('json',bill_details)
        return JsonResponse(bill_details_json)