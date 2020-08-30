from django.conf import settings

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, FileResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

import re
import uuid

import pandas as pd

from app.forms import DatasetUploadForm, TrainingForm, SaveModelForm, PredictForm
from app.models import Dataset, ClassificationModel

from app.data_functions import dataset_columns, data_checkboxes_in_columns, data_goal_in_columns, train_model, prediction, bugger

step=0


MEDIA_ROOT = settings.MEDIA_ROOT

# Create your views here.
def home(request):
    return render(request, "app/home.html")


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
            try:
                cd = datasetuploadform.cleaned_data
                #TODO heree add function that checks the dataset, like empty values...
                pd.read_excel(cd["dataset"])
                new_dataset = datasetuploadform.save(commit=False)
                new_dataset.name = str(cd["dataset"]).split(".")[0]
                new_dataset.owner = request.user
                new_dataset.save()
                messages.success(request, "Your dataset has been uploaded..")
            except:
                messages.error(request, "Your dataset is not suitable.")
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


@login_required
def dataset_download(request, dataset_id):
    dataset = get_object_or_404(Dataset, pk=dataset_id)
    if dataset.owner == request.user:
        file = open(MEDIA_ROOT + "/" + str(dataset.dataset), "rb")
        response = FileResponse(file, content_type='application/force-download')
        response['Content-Disposition'] = f'attachment; filename="{str(dataset.dataset)}"'
        return response
    else:
        return redirect("app:datasets")
 

@login_required
def training(request, dataset_id):
    context = {
        "dataset": None,
        "trainingform": None,
        "savemodelform": None,
        "dataset_columns": None,
        "training_acc": None,
        "test_acc": None,
    }
    
    dataset = get_object_or_404(Dataset, pk=dataset_id)

    if dataset.owner != request.user:
        return redirect("app:datasets")

    context["dataset"] = dataset
    context["dataset_columns"] = dataset_columns(dataset.dataset)

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
                messages.error(request, f"Your selected goal '{goal}' was in the selected variables. It was ommited in the training process.")

            # check if columns and goal in df, very unlikely, 
            #TODO put this all in train_model?
            column_with_type = data_checkboxes_in_columns(dataset.dataset, checkboxes)
            goal = data_goal_in_columns(dataset.dataset, goal)
            if (column_with_type == False) or (goal == False):
                messages.error(request, "It seems like your selection does not align with the provided dataset.")
                return render(request, "app/training.html", context)

            # refill form
            context["trainingform"] = trainingform

            train_results = train_model(request, dataset.dataset, column_with_type, goal)
            if train_results == False:
                messages.error(request, "Something went wrong during the training.")
                return render(request, "app/training.html", context)
            else:
                model_pk, training_acc, test_acc = train_results
                messages.success(request, "Training was succesful.")
            
            context["training_acc"] = round(training_acc, 5) * 100
            context["test_acc"] = round(test_acc, 5) * 100

            savemodelform = SaveModelForm(initial={"model_pk": model_pk})
            context["savemodelform"] = savemodelform
    return render(request, "app/training.html", context)

@login_required
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
def model_download(request, model_id):
    model = get_object_or_404(ClassificationModel, pk=model_id)
    if model.owner == request.user:
        file = open(str(model.trained_model), "rb")
        response = FileResponse(file, content_type='application/force-download')
        print(str(model.trained_model))
        response['Content-Disposition'] = f'attachment; filename="{str(model.dataset)}-{str(model.created)}.joblib"'
        return response
    else:
        return redirect("app:models")


@login_required 
def predict(request, model_id):

    context = {
        "model": None,
        "predictform": None,
        "predictionresult": None,
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
            context["predictionresult"] = prediction_result
            context["predictform"] = predictform
            
    return render(request, "app/predict.html", context)
    