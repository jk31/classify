from django.urls import path

from . import views

app_name = "app"
urlpatterns = [
    path("", views.home, name="home"),
    path("create-model", views.create_model, name="create_model"),
    path("model-created", views.model_created, name="model_created"),
]