from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('hell/', views.say_hello),
    path('view/',views.my_view , name='my-view'),
    path('idk/',views.idk),
    path('test/',views.test)
]+ static(settings.STATIC_URL)