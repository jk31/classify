from django.shortcuts import render
from django.http import HttpResponse

import pandas as pd

from .forms import UploadFileForm

# Create your views here.
def home(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            print("form valid")
            df = pd.read_csv(request.FILES['data'])
            print(df.info())
        else:
            print("form invalid")
    else:
        form = UploadFileForm()
    return render(request, "app/home.html", {"form": form})
