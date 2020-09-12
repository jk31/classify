import re
import tempfile
from joblib import dump, load

import pandas as pd
from sklearn import tree
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

import boto3

from django.conf import settings

from app.models import Dataset, ClassificationModel

MEDIA_ROOT = settings.MEDIA_ROOT

s3 = boto3.resource('s3')
bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)


def dataset_columns(dataset):
    """Return a dictionairy with the dataset columns and the respective type."""
    df = pd.read_excel(dataset.dataset.url)
    return dict(zip(df.columns, ["Numerical" if str(x) in ["int64", "float64"] else "Choice" for x in df.dtypes.values]))


def data_checkboxes_in_columns(dataset, checkboxes):
    """Checks if the checkboxes from the training request are actually in the dataset and if true, return columns with the types, otherwise return False"""
    try:
        df = pd.read_excel(dataset.dataset.url)
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


def data_goal_in_columns(dataset, goal):
    """Checks if the goal from the training request are actually in the dataset and if true, return the goal, otherwise return False"""
    try:
        df = pd.read_excel(dataset.dataset.url)
        if goal not in df.columns:
            return False
        else:
            return goal
    except:
        return False


def train_model(request, dataset, column_with_type, goal):
    """Train the model and save it, also takes care of the deletion of not saved models"""
    try:
        df = pd.read_excel(dataset.dataset.url)
        # keep only variables and goal
        keep = list(column_with_type.keys()) + [goal]
        df = df[keep]
        # to dummy variables
        to_dummy = [x for x in column_with_type if column_with_type[x] != "Numerical"]
        df = pd.get_dummies(df, columns=to_dummy)
        # split and training
        x_df_train, x_df_test, y_df_train, y_df_test = train_test_split(
                                                    df.drop(goal, axis=1),
                                                    df[goal],
                                                    test_size=0.2,
                                                    random_state=42)
        model = tree.DecisionTreeClassifier()
        model = model.fit(x_df_train, y_df_train)
        # return accuracy
        training_acc = model.score(x_df_train, y_df_train)
        test_acc = model.score(x_df_test, y_df_test)

        associated_dataset = Dataset.objects.get(dataset=dataset.dataset)

        new_model = ClassificationModel(
            owner=request.user,
            dataset=associated_dataset, 
            training_columns={"training_columns" : list(x_df_train.columns)}, 
            variables=column_with_type,
            goal=goal,
            training_acc=training_acc, 
            test_acc=test_acc)

        new_model.save()

        key = f"models/model_{new_model.pk}.joblib"

        with tempfile.TemporaryFile() as fp:
            dump(model, fp)
            fp.seek(0)
            bucket.put_object(Body=fp.read(), Key="media/" + key)

        #dump(model, f"{MEDIA_ROOT}/models/model_{new_model.pk}.joblib")
        new_model.trained_model = key

        new_model.save()

        return new_model.pk
    except:
        return False
    

def prediction(cd, model):
    """Make prediction and return result"""
    try:
        df_cd = pd.DataFrame([cd])

        training_columns = model.training_columns
        
        df_predict = pd.DataFrame(columns=training_columns["training_columns"])
        df_predict = df_predict.append(pd.get_dummies(df_cd))
        df_predict = df_predict.fillna(0)

        with tempfile.TemporaryFile() as fp:
            bucket.download_fileobj(Fileobj=fp, Key="media/" + str(model.trained_model))
            fp.seek(0)
            prediction_model = load(fp)

            prediction = prediction_model.predict(df_predict.iloc[0,:].values.reshape(1, -1))
            return str(prediction[0])
    except:
        return False



