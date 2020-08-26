from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings

import re
import uuid

import pandas as pd
from sklearn import tree
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from joblib import dump, load


from app.forms import UploadFileForm, PredictForm
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
                return False
        variable_options = {}
        for checkbox in checkboxes:
            if df[checkbox].dtypes == "object":
                variable_options.update({checkbox: sorted(df[checkbox].unique(), reverse=True)})
            else:
                variable_options.update({checkbox: "Numerical"})
        return variable_options
    except:
        return False

def data_goal_in_columns(id, goal):
    try:
        df = pd.read_excel(f"{MEDIA_ROOT}/{Dataset.objects.get(pk=id).dataset}")
        if goal not in df.columns:
            return False
        else:
            return goal
    except:
        return False

def train_model(id, column_with_type, goal):
    try:
        df = pd.read_excel(f"{MEDIA_ROOT}/{Dataset.objects.get(pk=id).dataset}")
        print("read df")
        print("after read df", df.head())
        keep = list(column_with_type.keys()) + [goal]
        df = df[keep]
        print("before get dummies")
        print(df.head())
        to_dummy = [x for x in column_with_type if column_with_type[x] != "Numerical"]
        df = pd.get_dummies(df, columns=to_dummy)
        print(df.head())
        x_df_train, x_df_test, y_df_train, y_df_test = train_test_split(
                                                    df.drop(goal, axis=1),
                                                    df[goal],
                                                    test_size=0.2,
                                                    random_state=42)
        print("split")
        model = tree.DecisionTreeClassifier()
        print("before fit")
        print(x_df_train.shape, y_df_train.shape)
        model = model.fit(x_df_train, y_df_train)
        training_acc = model.score(x_df_train, y_df_train)
        test_acc = model.score(x_df_test, y_df_test)
        print("before dump")
        dump(model, f"{MEDIA_ROOT}/model_{id}.joblib")

        return training_acc, test_acc, x_df_train.columns
    except:
        return False
    

# Create your views here.
def home(request):

    context = {
        "form": None, 
        "data_broken": None,
        "uploaded_no_training": None,
        "trained": None
    }

    # Upload file from main page
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

    dataset_id = request.session.get('dataset_id')
    if dataset_id != None:
        try:
            ClassificationModel.objects.get(trained_model=f"model_{dataset_id}.joblib")
            context["trained"] = True
        except:
            context["uploaded_no_training"] = True


    # if (request.session.get('dataset_id') != None) and :
    #     context["create_model_available"] = True

    return render(request, "app/home.html", context)

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

            new_model = ClassificationModel(dataset=dataset, training_columns={"training_columns" : list(training_columns)}, variables=column_with_type, goal=goal,
                                                trained_model=f"model_{dataset_id}.joblib", training_acc=training_acc, test_acc=test_acc)
            new_model.save()

            context["model_created"] = True
        except:
            return HttpResponse("something went wrong")
        
        return redirect("app:predict")

    return render(request, "app/create_model.html", context)
    
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
            # move the "field_" prefix
            cd = {re.match(f"field_(.*)", x)[1] : cd[x] for x in cd}
            df_cd = pd.DataFrame([cd])

            training_columns = model.training_columns
            
            df_predict = pd.DataFrame(columns=training_columns["training_columns"])
            df_predict = df_predict.append(pd.get_dummies(df_cd))
            df_predict = df_predict.fillna(0)

            prediction_model = load(f"{MEDIA_ROOT}/model_{dataset_id}.joblib")
            prediction = prediction_model.predict(df_predict.iloc[0,:].values.reshape(1, -1))
            context["prediction"] = str(prediction[0])
        
        context["form"] = form
            
    return render(request, "app/predict.html", context)


    