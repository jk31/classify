from django.urls import path

from . import views

app_name = "app"
urlpatterns = [
    path("", views.home, name="home"),
    path("demo-heart", views.demo_heart, name="demo_heart"),
    path("datasets", views.datasets, name="datasets"),
    path("datasets/delete/<int:dataset_id>", views.dataset_delete, name="dataset_delete"),
    path("datasets/download/<int:dataset_id>", views.dataset_download, name="dataset_download"),
    path("training/<int:dataset_id>", views.training, name="training"),
    path("models", views.models, name="models"),
    path("models/delete/<int:model_id>", views.model_delete, name="model_delete"),
    path("model/download/<int:model_id>", views.model_download, name="model_download"),
    path("save-model", views.save_model, name="save_model"),
    path("predict/<int:model_id>", views.predict, name="predict"),
]