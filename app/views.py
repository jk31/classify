from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings

import re
import uuid

import pandas as pd

from app.forms import UploadFileForm
from app.models import Dataset, ClassificationModel

MEDIA_ROOT = settings.MEDIA_ROOT

def data_show_columns(id):
    try:
        df = pd.read_excel(f"{MEDIA_ROOT}/{Dataset.objects.get(pk=id).dataset}")
        return dict(zip(df.columns, ["Numerical" if str(x) in ["int64", "float64"] else "Choice" for x in df.dtypes.values]))
    except:
        return False

def data_checkboxes_in_columns(id, checkboxes):
    try:
        df = pd.read_excel(f"{MEDIA_ROOT}/{Dataset.objects.get(pk=id).dataset}")
        for checkbox in checkboxes:
            if checkbox not in df.columns:
                print("checkbox not in df.columns")
                return False
        variable_options = {}
        for checkbox in checkboxes:
            if df[checkbox].dtypes == "object":
                print("checkbox is object")
                variable_options.update({checkbox: sorted(df[checkbox].unique(), reverse=True)})
                print("variable_options updated")
            else:
                print("checkbox is not object")
                variable_options.update({checkbox: "Numerical"})
                print("variable_options updated")
        return variable_options
    except:
        return False

# Create your views here.
def home(request):

    context = {
        "form": None, 
        "data_broken": None,
        "create_model_available": None,
    }

    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                pd.read_excel(request.FILES['data'])
                id = uuid.uuid4()
                new_dataset = Dataset(id=id, dataset = request.FILES['data'])
                new_dataset.save()
                request.session["dataset_id"] = str(id)
                return redirect("app:create_model")
            except:
                context["data_broken"] = True
                
    form = UploadFileForm()
    context["form"] = form

    if request.session.get('dataset_id') != None:
        context["create_model_available"] = True

    return render(request, "app/home.html", context)

def create_model(request):
    dataset_id = request.session.get('dataset_id')
    context = {
        "data_columns": None,
    }

    if dataset_id == None:
        return redirect("app:home")
    else:
        context["data_columns"] = data_show_columns(dataset_id)

    return render(request, "app/create_model.html", context)
    
def model_created(request):
    dataset_id = request.session.get('dataset_id')
    if request.method == "POST":
        # filter the names from the checkbox request
        checkboxes = [re.search(r"\-(.*)", checkbox)[1] for checkbox in request.POST.getlist("checkbox")]
        # check if names apear in dataframe
        if dataset_id == None:
            return redirect("app:home")
        else:
            column_with_type = data_checkboxes_in_columns(dataset_id, checkboxes)
            dataset = Dataset.objects.get(id=dataset_id)
            new_model = ClassificationModel(dataset=dataset, variables=column_with_type)
            new_model.save()
        # save selection with possible values
        return HttpResponse("OKI DOKI")
    else: 
        return HttpResponse("go back where you belong to")

    