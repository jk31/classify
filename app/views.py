from django.shortcuts import render
from django.http import HttpResponse

import pandas as pd

from .forms import UploadFileForm

# Create your views here.
def home(request):
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            df = pd.read_csv(request.FILES['data'])
            data_columns = dict(zip(df.columns, [str(x) for x in df.dtypes.values]))
            return render(request, "app/home.html", {"form": form, "data_columns": data_columns})
        else:
            print("###### form invalid #####")
    else:
        form = UploadFileForm()
    return render(request, "app/home.html", {"form": form})
