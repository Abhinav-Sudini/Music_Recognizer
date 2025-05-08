from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('hell/', views.say_hello),
    path('view/',views.my_view , name='my-view'),
    path('idk/',views.idk),
    path('test/',views.test),
    path('upload-audio/', views.upload_audio)
]+ static(settings.STATIC_URL)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

