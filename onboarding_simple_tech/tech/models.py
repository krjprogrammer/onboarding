from django.db import models
from django.contrib.postgres.fields import ArrayField

class Company(models.Model):
    name = models.CharField(max_length=255)
    website = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=20)
    tax_id = models.CharField(max_length=20)
    address = models.TextField()
    dm_first_name = models.CharField(max_length=255)
    dm_last_name = models.CharField(max_length=255)
    dm_mobile_number = models.CharField(max_length=20)
    sales_agent_number = models.CharField(max_length=20)
    sales_agent_details = models.TextField()
    notes = models.TextField()
    user_list = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    vendor_list = models.TextField()
    Payment_Type = models.CharField(max_length=100)


class base_data_table(models.Model):
    Date_Due = models.CharField(max_length=255,blank=True,default=None)
    AccountNumber = models.CharField(max_length=255,blank=True,default=None)
    InvoiceNumber = models.CharField(max_length=255,blank=True,default=None)
    Invoice_Method = models.CharField(max_length=255,default='NA')
    Payment_Type = models.CharField(max_length=255,default='NA')
    Website = models.CharField(max_length=255,blank=True,default=None)
    Total_Current_Charges = models.CharField(max_length=255,blank=True,default=None)
    Duration = models.CharField(max_length=255,blank=True,default=None)
    Bill_Date = models.CharField(max_length=255,blank=True,default=None)
    Client_Address = models.CharField(max_length=255,blank=True,default=None)
    Remidence_Address = models.CharField(max_length=255,blank=True,default=None)
    Billing_Name = models.CharField(max_length=255,blank=True,default=None)
    Billing_Address = models.CharField(max_length=255,blank=True,default=None)
    company = models.CharField(max_length=255,blank=True,default=None)
    vendor = models.CharField(max_length=255,blank=True,default=None)

class pdf_data_table(models.Model):
    Wireless_number = models.CharField(max_length=100, default='NA')
    User_name = models.CharField(max_length=100, default='NA')
    Monthly_Charges = models.CharField(max_length=100, default='NA')
    Usage_and_Purchase_Charges = models.CharField(max_length=100, default='NA')
    Equipment_Charges = models.CharField(max_length=100, default='NA')
    Surcharges_and_Other_Charges_and_Credits = models.CharField(max_length=100, default='NA')
    Taxes_Governmental_Surcharges_and_Fees = models.CharField(max_length=100, default='NA')
    Third_Party_Charges_includes_Tax = models.CharField(max_length=100, default='NA')
    Total_Charges = models.CharField(max_length=100, default='NA')
    Voice_Plan_Usage = models.CharField(max_length=100, default='NA')
    Messaging_Usage = models.CharField(max_length=100, default='NA')
    Data_Usage = models.CharField(max_length=100, default='NA')
    Account_number = models.CharField(max_length=100, default='NA')
    Plans = models.CharField(max_length=100, default='NA')

class merged_table(models.Model):
    Wireless_number = models.CharField(max_length=100, default='NA',blank=True)
    User_name_y = models.CharField(max_length=100, default='NA',blank=True)
    Monthly_Charges = models.CharField(max_length=100, default='NA',blank=True)
    Usage_and_Purchase_Charges = models.CharField(max_length=100, default='NA',blank=True)
    Equipment_Charges = models.CharField(max_length=100, default='NA',blank=True)
    Surcharges_and_Other_Charges_and_Credits = models.CharField(max_length=100, default='NA',blank=True)
    Taxes_Governmental_Surcharges_and_Fees = models.CharField(max_length=100, default='NA',blank=True)
    Third_Party_Charges_includes_Tax = models.CharField(max_length=100, default='NA',blank=True)
    Total_Charges = models.CharField(max_length=100, default='NA',blank=True)
    Voice_Plan_Usage = models.CharField(max_length=100, default='NA',blank=True)
    Messaging_Usage = models.CharField(max_length=100, default='NA',blank=True)
    Data_Usage = models.CharField(max_length=100, default='NA',blank=True)
    Account_number_y = models.CharField(max_length=100, default='NA',blank=True)
    Plans = models.CharField(max_length=100, default='NA',blank=True)
    Early_upgrade_indicator = models.CharField(max_length=100, default='NA',blank=True)
    Shipped_device_ID = models.CharField(max_length=100, default='NA',blank=True)
    Current_device_ID_4G_only = models.CharField(max_length=100, default='NA',blank=True)
    SIM = models.CharField(max_length=100, default='NA',blank=True)
    Device_manufacturer = models.CharField(max_length=100, default='NA',blank=True)
    Device_model = models.CharField(max_length=100, default='NA',blank=True)
    Device_type = models.CharField(max_length=100, default='NA',blank=True)
    Upgrade_eligibility_date = models.CharField(max_length=100, default='NA',blank=True)
    NE2_date = models.CharField(max_length=100, default='NA',blank=True)
    Account_number_x = models.CharField(max_length=100, default='NA',blank=True)
    Email_address = models.CharField(max_length=100, default='NA',blank=True)
    Cost_center = models.CharField(max_length=100, default='NA',blank=True)
    User_name_x = models.CharField(max_length=100, default='NA',blank=True)
    IP_address = models.CharField(max_length=100, default='NA',blank=True)
    Pool_name = models.CharField(max_length=100, default='NA',blank=True)
    IP_category = models.CharField(max_length=100, default='NA',blank=True)
    Contract_activation_date = models.CharField(max_length=100, default='NA',blank=True)
    Contract_end_date = models.CharField(max_length=100, default='NA',blank=True)
    Parent_MDN = models.CharField(max_length=100, default='NA',blank=True)
    Auto_Port_Indicator = models.CharField(max_length=100, default='NA',blank=True)
    Connected_device = models.CharField(max_length=100, default='NA',blank=True)
    Sim_Type = models.CharField(max_length=100, default='NA',blank=True)
    User_ID = models.CharField(max_length=100, default='NA',blank=True)
    Activation_date = models.CharField(max_length=100, default='NA',blank=True)
    company = models.CharField(max_length=100,default='NA')
    vendor = models.CharField(max_length=255,default='NA')

class MappingData(models.Model):
    Wireless_number = models.CharField(max_length=100, default='NA')
    User_name = models.CharField(max_length=100, default='NA')
    Monthly_Charges = models.CharField(max_length=100, default='NA')
    Surcharges_and_Other_Charges_and_Credits = models.CharField(max_length=100, default='NA')
    Third_Party_Charges_includes_Tax = models.CharField(max_length=100, default='NA')
    Total_Charges = models.CharField(max_length=100, default='NA')
    Plans = models.CharField(max_length=100, default='NA')
    Current_device_ID_4G_only = models.CharField(max_length=100, default='NA')
    SIM = models.CharField(max_length=100, default='NA')
    Device_model = models.CharField(max_length=100, default='NA')
    Cost_center = models.CharField(max_length=100, default='NA')
    Sim_Type = models.CharField(max_length=100, default='NA')
    Account_number = models.CharField(max_length=100, default='NA')

class Vendor_data_table(models.Model):
    company = models.CharField(max_length=100,default='NA')
    vendor = models.CharField(max_length=100,default='NA')


class Column_mapping_data(models.Model):
    columns = models.CharField(max_length=1000)

class Portal_information_data(models.Model):
    URL = models.CharField(max_length=1000)
    Username = models.CharField(max_length=250)
    Password = models.CharField(max_length=250)
    Customer_Name = models.CharField(max_length=250)
    Vendor = models.CharField(max_length=250)
    Account_number = models.CharField(max_length=250)
    User_email_id = models.CharField(max_length=250)
    Automated = models.CharField(max_length=250)
    On_Email = models.CharField(max_length=250)

class user_pdf(models.Model):
    acc_no = models.CharField(max_length=255)
    bill_date = models.CharField(max_length=255)
    pdf = models.FileField(upload_to='pdfs/')

class contract_table(models.Model):
    contract_filename = models.CharField(max_length=255)
    contract_pdf_path = models.FileField(upload_to='contracts/')