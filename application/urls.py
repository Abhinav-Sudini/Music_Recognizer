from django.urls import path
from . import views


urlpatterns = [
    path('hell/', views.say_hello),
    path('view/',views.my_view , name='my-view'),
    path('idk/',views.idk),
    path('test/',views.test)
]