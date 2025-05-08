import os
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import song
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.conf import settings
from pydub import AudioSegment


# Create your views here.

def say_hello(request):
    

    return render(request,'index.html')

def idk(request):
    return HttpResponse("hi bro")

@csrf_exempt
def upload_audio(request):
    print("hi")
    if request.method == 'POST' and request.FILES.get('audio'):
        audio_file = request.FILES['audio']

        # Save original webm
        temp_input_path = default_storage.save('temp/temp_input.wav', audio_file)
        input_path = os.path.join(settings.MEDIA_ROOT, temp_input_path)
        print("temp:",temp_input_path, "\ninp:",input_path)

        # DO PROCESSING 
        json_out = {'status': 'success'}
        # UNCOMMENT THIS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # json_out["song"] = find_song(temp_input_path)
        # Clean up temp file
        # default_storage.delete(temp_input_path)
        print(json_out)

        # example output comment this !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        json_out = {'status': 'success', 'song': {'song_id': 0, 'song_file': './media/songs/song4.wav', 'singer': 'me', 'song_name': ' Force Projection | Cyberpunk 2077', 'link': 'bSpQpImpZbw', 'time': 54}}
        return JsonResponse(json_out) #SEND TO FRONTEND