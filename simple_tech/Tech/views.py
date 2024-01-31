from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import company_serializer
from rest_framework import status
from .models import Company

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
        
