from django.urls import path
from . import views


urlpatterns = [
    path('hell/', views.say_hello),
    path('idk/',views.idk)
]