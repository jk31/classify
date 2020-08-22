from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings 


# Create your views here.
def home(request):
    return render(request, "app/home.html")
