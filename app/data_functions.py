from django.conf import settings

import re

import pandas as pd
from sklearn import tree
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from joblib import dump, load
from app.models import Dataset, ClassificationModel

MEDIA_ROOT = settings.MEDIA_ROOT

step = 0
def bugger():
    global step
    step += 1
    print("######", step)


def dataset_columns(dataset):
    """Return a dictionairy with the dataset columns and the respective type."""
    df = pd.read_excel(f"{MEDIA_ROOT}/{dataset}")
    return dict(zip(df.columns, ["Numerical" if str(x) in ["int64", "float64"] else "Choice" for x in df.dtypes.values]))


def data_checkboxes_in_columns(dataset, checkboxes):
    """Checks if the checkboxes from the training request are actually in the dataset and if true, return columns with the types, otherwise return False"""
    try:
        df = pd.read_excel(f"{MEDIA_ROOT}/{dataset}")
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
        df = pd.read_excel(f"{MEDIA_ROOT}/{dataset}")
        if goal not in df.columns:
            return False
        else:
            return goal
    except:
        return False


def train_model(dataset, column_with_type, goal):
    try:
        df = pd.read_excel(f"{MEDIA_ROOT}/{dataset}")
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
        # dump(model, f"{MEDIA_ROOT}/model_{id}.joblib")
        return dataset, column_with_type, goal, training_acc, test_acc, x_df_train.columns
    except:
        return False
    

def prediction(cd, model):
    # move the "field_" prefix
    cd = {re.match(f"field_(.*)", x)[1] : cd[x] for x in cd}
    df_cd = pd.DataFrame([cd])

    training_columns = model.training_columns
    
    df_predict = pd.DataFrame(columns=training_columns["training_columns"])
    df_predict = df_predict.append(pd.get_dummies(df_cd))
    df_predict = df_predict.fillna(0)

    prediction_model = load(f"{MEDIA_ROOT}/model_{dataset_id}.joblib")
    prediction = prediction_model.predict(df_predict.iloc[0,:].values.reshape(1, -1))

    return str(prediction[0])


