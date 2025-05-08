from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('hell/', views.say_hello),
    path('idk/',views.idk),
    path('upload-audio/', views.upload_audio)
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)