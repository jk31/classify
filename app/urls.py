from django.urls import path

from . import views

app_name = "app"
urlpatterns = [
    path("", views.home, name="home"),
    path("datasets", views.datasets, name="datasets"),
    path("models", views.models, name="models"),
    path("training/<int:dataset_id>", views.training, name="training"),
    path("save-model", views.save_model, name="save_model"),
    path("predict/<int:model_id>", views.predict, name="predict"),
]