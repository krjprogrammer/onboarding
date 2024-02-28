from rest_framework import serializers
from .models import Company,merged_table,pdf_data_table,base_data_table,MappingData,Vendor_data_table,Column_mapping_data,Portal_information_data
class company_serializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class bill_data_serializer(serializers.ModelSerializer):
    class Meta:
        model = merged_table
        exclude = ['Usage_and_Purchase_Charges', 'Equipment_Charges', 'Taxes_Governmental_Surcharges_and_Fees',
           'Voice_Plan_Usage', 'Messaging_Usage', 'Data_Usage', 'Account_number_y', 'Early_upgrade_indicator',
           'Shipped_device_ID', 'Device_manufacturer', 'Device_type', 'Upgrade_eligibility_date',
           'NE2_date', 'Email_address', 'User_name_x', 'IP_address', 'Pool_name', 'IP_category',
           'Contract_activation_date', 'Contract_end_date', 'Parent_MDN', 'Auto_Port_Indicator',
           'Connected_device', 'User_ID','Activation_date']
        
class mapping_serializer(serializers.ModelSerializer):
    class Meta:
        model = MappingData
        fields = '__all__'

class vendor_data_serializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor_data_table
        fields = '__all__'

class base_data_serializer(serializers.ModelSerializer):
    class Meta:
        model=base_data_table
        fields = '__all__'

class column_serializer(serializers.ModelSerializer):
    class Meta:
        model = Column_mapping_data
        fields = '__all__'

class portal_info_serializer(serializers.ModelSerializer):
    class Meta:
        model = Portal_information_data
        fields = '__all__'
