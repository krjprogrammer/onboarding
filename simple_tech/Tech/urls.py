from django.urls import path
from .views import post_company_data,comapany_api_view
urlpatterns = [
    path('post_company_data',post_company_data.as_view()),
    path('company_api_view',comapany_api_view.as_view())
]