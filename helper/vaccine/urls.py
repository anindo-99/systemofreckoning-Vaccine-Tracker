from django.urls import path
from . import views

urlpatterns = [
    path('', views.vaccineHome, name="vaccine"),

    path('handle_vaccine_slots/', views.handleVaccine,
         name="handle_vaccine_slots"),

]
