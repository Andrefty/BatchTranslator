from django.urls import path, re_path
from . import views

app_name = 'uiapp'

urlpatterns = [
    path('create/', views.EmailaddressCreateView.as_view(), name='emailaddress_create'),
]
