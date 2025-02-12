from django.urls import path
from .import views
app_name="store"

urlpatterns=[
    path("store/",views.index,name="index")
]