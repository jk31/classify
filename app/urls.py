from django.urls import path

from . import views

app_name = "app"
urlpatterns = [
    path("", views.home, name="home"),
    path("datasets", views.datasets, name="datasets"),
    path("models", views.models, name="models"),
    path("training/<int:dataset_id>", views.training, name="training"),
    path("create-model", views.create_model, name="create_model"),
    path("predict", views.predict, name="predict"),
]