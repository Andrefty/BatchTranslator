from django.urls import path, re_path
from . import views

# namespace
app_name = 'uiapp'

urlpatterns = [
    path('new/', views.QueryCreateView.as_view(), name='new')
]