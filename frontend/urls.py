from django.urls import path, include
from . import views

urlpatterns = [
    # FOR REACT JS:-
    path('', views.index)

]