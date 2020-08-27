from django.conf import settings

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

import re
import uuid

import pandas as pd

from app.forms import DatasetUploadForm, TrainingForm, PredictForm
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

    datasets = Dataset.objects.all().filter(owner__username=request.user)
    context["datasets"] = datasets

    if request.method == "POST":
        datasetuploadform = DatasetUploadForm(request.POST, request.FILES)
        if datasetuploadform.is_valid():
            try:
                cd = datasetuploadform.cleaned_data
                #TODO heree add function that checks the dataset, like empty values...
                pd.read_excel(cd["dataset"])
                new_dataset = datasetuploadform.save(commit=False)
                new_dataset.name = str(request.FILES['dataset']).split(".")[0]
                new_dataset.owner = request.user
                new_dataset.save()
            except:
                messages.error(request, "Your dataset is not suitable.")
    else:
        datasetuploadform = DatasetUploadForm()
        
    
    context["datasetuploadform"] = datasetuploadform
    return render(request, "app/datasets.html", context)


@login_required
def training(request, dataset_id):
    context = {
        "dataset": None,
        "trainingform": None,
        "dataset_columns": None,
        "training_acc": None,
        "test_acc": None,
    }
    
    dataset = get_object_or_404(Dataset, pk=dataset_id)

    if dataset.owner != request.user:
        print("not your dataset")
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
            print(column_with_type)
            goal = data_goal_in_columns(dataset.dataset, goal)
            if (column_with_type == False) or (goal == False):
                messages.error(request, "It seems like your selection does not align with the provided dataset.")
                return render(request, "app/training.html", context)

            # refill form
            context["trainingform"] = trainingform

            train_results = train_model(dataset.dataset, column_with_type, goal)
            if train_results == False:
                messages.error(request, "Something went wrong during the training.")
                return render(request, "app/training.html", context)
            else:
                dataset, column_with_type, goal, training_acc, test_acc, training_columns = train_results
                print(training_acc, test_acc)
                messages.success(request, "Training was succesful.")
            
            context["training_acc"] = round(training_acc, 4) * 100
            context["test_acc"] = round(test_acc, 4)* 100


            # new_model = ClassificationModel(dataset=dataset, 
            #                                 training_columns={"training_columns" : list(training_columns)}, 
            #                                 variables=column_with_type, 
            #                                 goal=goal,
            #                                 trained_model=f"model_{dataset_id}.joblib", 
            #                                 training_acc=training_acc, test_acc=test_acc)
            # new_model.save()


    return render(request, "app/training.html", context)


@login_required
def models(request):
    return HttpResponse("My Models")


def create_model(request):
    dataset_id = request.session.get('dataset_id')

    context = {
        "data_columns": None,
        "model_created": None,
        "training_acc": None,
        "test_acc": None,
    }

    if dataset_id == None:
        return redirect("app:home")
    else:
        context["data_columns"] = data_show_columns(dataset_id)

    try:
        ClassificationModel.objects.get(trained_model=f"model_{dataset_id}.joblib")
        return redirect("app:predict")
    except:
        pass

    if request.method == "POST":
        try:
            # clear request data
            checkboxes = [re.search(r"\-(.*)", checkbox)[1] for checkbox in request.POST.getlist("checkbox")]
            goal = re.search(r"\-(.*)", request.POST.get("radio"))[1]

            if goal in checkboxes:
                checkboxes.remove(goal)

            # check if columns in df and if yes save to ClassificationModel
            column_with_type = data_checkboxes_in_columns(dataset_id, checkboxes)
            goal = data_goal_in_columns(dataset_id, goal)
            dataset = Dataset.objects.get(id=dataset_id)
            print("before training")
            training_acc, test_acc, training_columns = train_model(dataset_id, column_with_type, goal)

            new_model = ClassificationModel(dataset=dataset, 
                                            training_columns={"training_columns" : list(training_columns)}, 
                                            variables=column_with_type, 
                                            goal=goal,
                                            trained_model=f"model_{dataset_id}.joblib", 
                                            training_acc=training_acc, test_acc=test_acc)
            new_model.save()

            context["model_created"] = True
        except:
            return HttpResponse("something went wrong")
        
        return redirect("app:predict")

    return render(request, "app/create_model.html", context)

@login_required 
def predict(request):
    dataset_id = request.session.get('dataset_id')
    if dataset_id == None:
            return redirect("app:home")

    context = {
        "model_created": None,
        "training_acc": None,
        "test_acc": None,
        "form": None,
        "prediction": None,
    }

    try:
        model = ClassificationModel.objects.get(trained_model=f"model_{dataset_id}.joblib")
        context["model_created"] = True
        context["training_acc"] = round(float(model.training_acc), 3) * 100
        context["test_acc"] = round(float(model.test_acc), 3) * 100
    except:
        return redirect("app:home")

    form = PredictForm(model.variables)
    context["form"] = form

    if request.method == "POST":
        form = PredictForm(model.variables, request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            context["prediction"] = prediction(cd, model)
        
        context["form"] = form
            
    return render(request, "app/predict.html", context)
    