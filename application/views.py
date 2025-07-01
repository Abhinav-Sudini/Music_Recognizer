from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.shortcuts import render,redirect
from scipy.signal import find_peaks
from django.db import connection
from django.conf import settings
from itertools import islice
from queue import Queue
import time
import os

#for hashing and visualizing audio files 
import xxhash
import librosa
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


from .models import song,user_file,fingerprint
from .form import DocumentForm
from .functions import *
from .find_song import *
from .db import *

# Create your views here.

def home(request):
    message = 'Upload files!'
    
    # Handle file upload
    context = { 'message': message}

    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            audio_file = request.FILES['docfile']
            temp_input_path = default_storage.save('temp/temp_input.wav', audio_file)
            input_path = os.path.join(settings.MEDIA_ROOT, temp_input_path)
            print("temp:",temp_input_path, "\ninp:",input_path)

            context["song"] = find_song(temp_input_path,"file")

            print(context)
            default_storage.delete(input_path)
            # Redirect to the document list after POST
        else:
            message = 'The form is not valid. Fix the following error:'
    else:
        form = DocumentForm() 
    context['form'] = form

    return render(request, 'index.html',context)

@csrf_exempt
def upload_audio(request):
    print("hi")
    json_out = {}
    if request.method == 'POST' and request.FILES.get('audio'):
        audio_file = request.FILES['audio']

        # Save original webm
        temp_input_path = default_storage.save('temp/temp_input.wav', audio_file)
        input_path = os.path.join(settings.MEDIA_ROOT, temp_input_path)
        print("temp:",temp_input_path, "\ninp:",input_path)

        # DO PROCESSING 
        json_out["song"] = find_song(temp_input_path,"audio")
        json_out = {'status': 'success'}
        default_storage.delete(input_path)
    else:
        json_out = {'status': 'fail'}

    print(json_out)
    # example output
    # {'status': 'success', 'song': {'song_id': 0, 'song_file': './media/songs/song4.wav', 'singer': 'me', 'song_name': ' Force Projection | Cyberpunk 2077', 'link': 'bSpQpImpZbw', 'time': 54}}
    return JsonResponse(json_out) #SEND TO FRONTEND


def add_songs_db(request):
    song_id = 0
    audio_fpath = "./media/songs/"
    audio_clips = os.listdir(audio_fpath)
    songs_dataframe = pd.read_excel('./song.xlsx')
    print(songs_dataframe)

    for index,row in songs_dataframe.iterrows():
        song_path = row["file"]
        new_song = song(song_id=song_id,song_file=audio_fpath+song_path,
                        singer=row["singer"],song_name=row["song_name"],link=row["link"])
        new_song.save()
        add_to_db(audio_fpath+song_path,new_song)
        song_id+=1
        print("done with ",song_path)
           
    # print("hi"*10)
    return HttpResponse("done bro")


def test_songs(request):
    paths = ["song1_c.wav","song1_m.wav","song1_wec.wav","song1_ml.wav","song1_mll.wav","song2_sc.wav","song2_m.wav","song4_ml.wav","song4_webc.wav","song4_webs.wav","song4_web_sri.wav","song4_web_rec.wav"]
    temp = {}
    for path in paths:
        print(path,".............")
        top_song = (find_song(path))

        temp[path] = top_song

    return render(request, 'temp.html',{"songs":temp})



    