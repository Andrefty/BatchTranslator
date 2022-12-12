from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .models import Email
from .forms import EmailForm

# Create your views here.

class QueryCreateView(CreateView):
    model = Email
    form_class = EmailForm
    success_url = reverse_lazy('uiapp:new')