from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('home/',views.home , name='my-view'),
    path('test/',views.test_songs),
    path('add_songs_db/', views.add_songs_db),
    path('upload-audio/', views.upload_audio)
]+ static(settings.STATIC_URL)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

