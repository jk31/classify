import re
import uuid

from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, FileResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ratelimit.decorators import ratelimit

import pandas as pd

from app.forms import DatasetUploadForm, TrainingForm, SaveModelForm, PredictForm
from app.models import Dataset, ClassificationModel
from app.data_functions import dataset_columns, data_checkboxes_in_columns, data_goal_in_columns, train_model, prediction

MEDIA_ROOT = settings.MEDIA_ROOT

# Create your views here.
def home(request):
    return render(request, "app/home.html")

def beta(request):
    return render(request, "app/beta.html")

def demo_churn(request):
    context = {
        "model": None,
        "predictform": None,
        "predictionresult": None,
        "input": None,
    }

    model = get_object_or_404(ClassificationModel, pk=1)
    context["model"] = model

    predictform = PredictForm(model.variables)
    context["predictform"] = predictform

    if request.method == "POST":
        predictform = PredictForm(model.variables, request.POST)
        if predictform.is_valid():
            cd = predictform.cleaned_data
            prediction_result = prediction(cd, model)
            if prediction_result == False:
                messages.warning(request, "Something went wrong with the prediction.")
            else:
                context["predictionresult"] = prediction_result
                context["predictform"] = predictform
                context["input"] = cd
        else:
            messages.warning(request, "Something went wrong with the prediction.")
      
    return render(request, "app/predict.html", context)

def demo_heart(request):
    context = {
        "model": None,
        "predictform": None,
        "predictionresult": None,
        "input": None,
    }

    model = get_object_or_404(ClassificationModel, pk=2)
    context["model"] = model

    predictform = PredictForm(model.variables)
    context["predictform"] = predictform

    if request.method == "POST":
        predictform = PredictForm(model.variables, request.POST)
        if predictform.is_valid():
            cd = predictform.cleaned_data
            prediction_result = prediction(cd, model)
            if prediction_result == False:
                messages.warning(request, "Something went wrong with the prediction.")
            else:
                context["predictionresult"] = prediction_result
                context["predictform"] = predictform
                context["input"] = cd
        else:
            messages.warning(request, "Something went wrong with the prediction.")
      
    return render(request, "app/predict.html", context)

@login_required
def datasets(request):

    context = {
        "datasets": None,
        "datasetuploadform": None,
    }

    datasets = Dataset.objects.filter(owner=request.user)
    context["datasets"] = datasets

    if request.method == "POST":
        datasetuploadform = DatasetUploadForm(request.POST, request.FILES)
        if datasetuploadform.is_valid():
            # try:
            cd = datasetuploadform.cleaned_data
            #TODO heree add function that checks the dataset, like empty values...
            pd.read_excel(cd["dataset"])
            new_dataset = datasetuploadform.save(commit=False)
            new_dataset.name = str(cd["dataset"]).split(".")[0]
            new_dataset.owner = request.user
            new_dataset.save()
            messages.success(request, "Your dataset has been uploaded.")
            # except:
            #     messages.warning(request, "Your dataset is not suitable.")
    else:
        datasetuploadform = DatasetUploadForm()
        
    
    context["datasetuploadform"] = datasetuploadform
    return render(request, "app/datasets.html", context)

@login_required
def dataset_delete(request, dataset_id):
    if request.method == "POST":
        dataset = get_object_or_404(Dataset, pk=dataset_id)
        if dataset.owner == request.user:
            dataset.dataset.delete()
            dataset.delete()
            messages.success(request, "Dataset deleted.")
    return redirect("app:datasets")


# @login_required
@ratelimit(key='ip', rate='100/h')
def dataset_download(request, dataset_id):
    dataset = get_object_or_404(Dataset, pk=dataset_id)
    if (dataset.owner == request.user) or (dataset_id in [1, 2]):
        return redirect(dataset.dataset.url)
    else:
        return redirect("app:home")
        
@login_required
@ratelimit(key='ip', rate='100/h')
def training(request, dataset_id):
    context = {
        "dataset": None,
        "trainingform": None,
        "savemodelform": None,
        "dataset_columns": None,
        "new_model": None,
    }
    
    dataset = get_object_or_404(Dataset, pk=dataset_id)

    if dataset.owner != request.user:
        return redirect("app:datasets")

    context["dataset"] = dataset
    context["dataset_columns"] = dataset_columns(dataset)

    trainingform = TrainingForm(context["dataset_columns"])
    context["trainingform"] = trainingform

    if request.method == "POST":
        trainingform = TrainingForm(context["dataset_columns"], request.POST)
        if trainingform.is_valid():
            cd = trainingform.cleaned_data
            # clear request data
            checkboxes = [re.search(r"\_(.*)", checkbox).group(1) for checkbox in cd if re.search(r"\_(.*)", checkbox) and cd[checkbox] == True]
            goal = cd["goal"]

            #TODO make this not possible in the frontend
            if goal in checkboxes:
                checkboxes.remove(goal)
                messages.warning(request, f"Your selected goal '{goal}' was in the selected variables. It was ommited in the training process.")

            # check if columns and goal in df, very unlikely, 
            #TODO put this all in train_model?
            column_with_type = data_checkboxes_in_columns(dataset, checkboxes)
            goal = data_goal_in_columns(dataset, goal)
            if (column_with_type == False) or (goal == False):
                messages.warning(request, "It seems like your selection does not align with the provided dataset.")
                return render(request, "app/training.html", context)

            # refill form
            context["trainingform"] = trainingform

            train_results = train_model(request, dataset, column_with_type, goal)
            if train_results == False:
                messages.warning(request, "Something went wrong during the training.")
                return render(request, "app/training.html", context)
            else:
                model_pk = train_results
                new_model = get_object_or_404(ClassificationModel, pk=model_pk)
                context["new_model"] = new_model
                savemodelform = SaveModelForm(initial={"model_pk": model_pk})
                context["savemodelform"] = savemodelform

                messages.success(request, "Training was succesful.")

    return render(request, "app/training.html", context)

@login_required
@ratelimit(key='ip', rate='100/h')
def save_model(request):
    if request.method == "POST":
        savemodelform = SaveModelForm(request.POST)
        if savemodelform.is_valid():
            cd = savemodelform.cleaned_data
            model_pk = cd["model_pk"]
            saved_model = ClassificationModel.objects.get(pk=model_pk)

            if saved_model.owner != request.user:
                return redirect("app:datasets")

            saved_model.saved = True
            saved_model.save()

            # delete classification models that belong to the user, but are not saved.
            remove_not_saved = ClassificationModel.objects.filter(owner=request.user, saved=False)
            for model in remove_not_saved:
                model.trained_model.delete()
            
            remove_not_saved.delete()
            return redirect("app:models")
        else:
            return redirect("app:training")

@login_required
def models(request):
    context = {
        "models": None
    }
    models = ClassificationModel.objects.filter(owner=request.user, saved=True)
    context["models"] = models
    return render(request, "app/models.html", context)

@login_required
def model_delete(request, model_id):
    if request.method == "POST":
        model = get_object_or_404(ClassificationModel, pk=model_id)
        if model.owner == request.user:
            model.trained_model.delete()
            model.delete()
            messages.success(request, "Model deleted.")
    return redirect("app:models")

@login_required
@ratelimit(key='ip', rate='100/h')
def model_download(request, model_id):
    model = get_object_or_404(ClassificationModel, pk=model_id)
    if model.owner == request.user:
        return redirect(model.trained_model.url)

@login_required
@ratelimit(key='ip', rate='100/h')
def predict(request, model_id):

    context = {
        "model": None,
        "predictform": None,
        "predictionresult": None,
        "input": None,
    }

    model = get_object_or_404(ClassificationModel, pk=model_id)
    if model.owner != request.user:
        return redirect("app:models")
    context["model"] = model

    predictform = PredictForm(model.variables)
    context["predictform"] = predictform

    if request.method == "POST":
        predictform = PredictForm(model.variables, request.POST)
        if predictform.is_valid():
            cd = predictform.cleaned_data
            prediction_result = prediction(cd, model)
            if prediction_result == False:
                messages.warning(request, "Something went wrong with the prediction.")
            else:
                context["predictionresult"] = prediction_result
                context["predictform"] = predictform
                context["input"] = cd
        else:
            messages.warning(request, "Something went wrong with the prediction.")
      
    return render(request, "app/predict.html", context)