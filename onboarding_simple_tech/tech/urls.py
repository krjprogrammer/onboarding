from django.urls import path
from .views import post_company_data,comapany_api_view,total_base_data,bill_data_api,upload_file,upload_csv,current_bill_data,current_base_data_api,specific_company_data,get_column_names,vendor_data,post_mapping_data,get_mapping_data,post_portal_info,get_portal_info,post_edited_data,delete_ban,view_bills,view_attachment,view_contract_attachment,upload_contract,add_more_lines,bill_details
urlpatterns = [
    path('post_company_data',post_company_data.as_view()),
    path('company_api_view',comapany_api_view.as_view()),
    path('specific_company_data/<str:param>/',specific_company_data.as_view()),
    path('uploadfile',upload_file),
    path('uploadcsv',upload_csv),
    path('api-data',bill_data_api.as_view()),
    path('base_data_api',total_base_data.as_view()),
    path('current_bill-data/<str:acc_no>/',current_bill_data.as_view()),
    path('current_base_data',current_base_data_api.as_view()),
    path('get_columns',get_column_names.as_view()),
    path('get_vendor_data',vendor_data.as_view()),
    path('post_mapping_data',post_mapping_data.as_view()),
    path('get_mapping_data',get_mapping_data.as_view()),
    path('post_portal_info',post_portal_info.as_view()),
    path('get_portal_info',get_portal_info.as_view()),
    path('post_edited_data',post_edited_data.as_view()),
    path('delete_ban',delete_ban.as_view()),
    path('view_bills',view_bills.as_view()),
    path('view_attachment',view_attachment.as_view()),
    path('upload_contract',upload_contract),
    path('view_contract',view_contract_attachment.as_view()),
    path('add_more_lines',add_more_lines.as_view()),
    path('bill_details',bill_details.as_view())
]