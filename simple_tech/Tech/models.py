from django.db import models

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
