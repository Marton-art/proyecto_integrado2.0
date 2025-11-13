from miAppCalificacion import views
from django.urls import path

urlpatterns = [
    path('', views.home_cali, name='home'),
]