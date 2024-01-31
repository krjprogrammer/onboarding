from rest_framework import serializers
from .models import Company
class company_serializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'