import os
from django.shortcuts import render,redirect
from django.http import HttpResponse, JsonResponse
from .models import song,user_file,fingerprint
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.conf import settings
from .form import DocumentForm
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
from itertools import islice
#for loading and visualizing audio files
from django.db import connection
from .functions import *
from queue import Queue
import xxhash
import numpy as np
import pandas as pd
import librosa
import matplotlib.pyplot as plt

# Create your views here.

def find_hash(path):
    peaks = find_peak_fq(path)

    length = len(peaks)
    hashes = []
    for index in range(length):
        pt = 0
        temp = []
        fuz_fac = [1,2,3,5,10,20,35,50,60]
        for k in peaks[index]:
            temp.append((k))
            pt+=1
        
        str_fq = str(sorted(list(temp[:-1])))
        gen_hash = to_int(xxhash.xxh3_64_hexdigest(str_fq))
        hashes.append((gen_hash,index))

    return hashes

def add_to_db(path,new_song):

    hashes = find_hash(path)
    hashset = hashes
    print("need to add ",len(hashset))
    batch_size = 500
    objs = (fingerprint(hash=hsh,offset=off,song_id=new_song) for hsh,off in hashset)
    while True:
        batch = list(islice(objs, batch_size))
        if not batch:
            break
        fingerprint.objects.bulk_create(batch, batch_size)

    print("added - ",len(hashset))


def say_hello(request):
    
    # file = user_file.objects.get(pk=3)
    # print((file.docfile))
    # _delete_file(file.docfile.path)
    
    # file.delete()
    song_id = 0
    audio_fpath = "./media/songs/"
    audio_clips = os.listdir(audio_fpath)
    songs_dataframe = pd.read_excel('./song.xlsx')
    print(songs_dataframe)

    # print(songs_dataframe["file"].tolist())

    #for song_path in audio_clips:
    for index,row in songs_dataframe.iterrows():
        song_path = row["file"]
        new_song = song(song_id=song_id,song_file=audio_fpath+song_path,singer=row["singer"],song_name=row["song_name"],link=row["link"])
        new_song.save()
        add_to_db(audio_fpath+song_path,new_song)
        song_id+=1
        print("done with ",song_path)
           
    # print("hi"*10)
    return HttpResponse("done bro")

def to_int(st):
    return int(st[8:], 16)

def test(request):
    return HttpResponse("done bro")

def find_song(path,type="file"):
    hashs = find_hash("./media/"+path)
    hash_dict = make_dict(hashs)
    hash_set = [hsh for hsh,off in hashs]
    str_hash = str(hash_set)
    str_hash = str_hash[1:-1]
    top_song = {}

    
    for song_id in range(10):
        query = """
            SELECT hash, offset
            FROM test.application_fingerprint 
            WHERE hash in ( %s ) and song_id_id = %s order by offset;
        """ % (str_hash,song_id)

        matched_hsh = execute_raw_sql(query)

        length = len(matched_hsh)
        coherence_score=0
        sum_offset = 0
        temp_off = []
        values = []
        mini_off = 10000

        for i in range(length-10):
            hsh1,off1 =  matched_hsh[i]
            for j in range(1,5):

                hsh2,off2 = matched_hsh[i+j]
                user_off1 = hash_dict[hsh1]
                user_off2 = hash_dict[hsh2]
                dif_offeset = abs(off2-off1)
                flag = True

                for u_off1 in user_off1:
                    for u_off2 in user_off2:
                        if u_off1<u_off2 and abs(dif_offeset-(u_off2-u_off1))<4:
                            coherence_score+=1
                            sum_offset+= off1
                            values.append(off1)
                            mini_off = min(mini_off,off1)
                            temp_off.append(off1)
                            flag = False
                            break
                    if flag==False:
                        break


        song_time = -1
        if not coherence_score == 0:
            plt.figure().clear()
            plt.hist(values)
            plt.xlabel('weight')
            plt.ylabel('count')
            plt.savefig(f"foo{song_id}.png")
            if song_id in [5,6]:
                song_time = sum_offset/coherence_score - 2*len(hashs)
            else:
                song_time = sum_offset/coherence_score - len(hashs)/2

        
        top_song[song_id] = (coherence_score,song_time*0.0463)

    

    print(top_song)
    final_song = {"id":0,"time":0}
    max_match = 0

    for key,value in top_song.items():
        if value[0] > max_match:
            final_song["id"] = key
            final_song["time"] = value[1]
            max_match = value[0]

    query="""
    select *
    FROM test.application_song
    WHERE song_id = %s ;
""" % final_song["id"]
    
    output = execute_sql(query)[0]
    output["time"] = max(0,int(final_song["time"]))

    print(output)
    return output

def idk(request):
    paths = ["song1_c.wav","song1_m.wav","song1_wec.wav","song1_ml.wav","song1_mll.wav","song2_sc.wav","song2_m.wav","song4_ml.wav","song4_webc.wav","song4_webs.wav","song4_web_sri.wav","song4_web_rec.wav"]
    temp = {}
    for path in paths:
        print(path,".............")
        top_song = (find_song(path))

        temp[path] = top_song

    return render(request, 'temp.html',{"songs":temp})

def _delete_file(path):
    # Deletes file from filesystem.
    if os.path.isfile(path):
        os.remove(path)

def my_view(request):
    message = 'Upload as many files as you want!'
    
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
            # Clean up temp file
            # default_storage.delete(temp_input_path)
            print(context)
            default_storage.delete(input_path)

            # Redirect to the document list after POST
        else:
            message = 'The form is not valid. Fix the following error:'
    else:
        form = DocumentForm() 
    context['form'] = form

    return render(request, 'index.html',context)

def find_pe(X,nfft,SR):
    freqs = librosa.fft_frequencies(sr=SR,n_fft=nfft)
    ranges = [20,40,80,160,180,300,600,5000,2000000]
    fuz_fac = [1,2,4,6,6,8,8,12,4,5,5,5,10]
    peak = [0 for j in range(len(ranges))]
    pt = 0
    index = 0
    for i in freqs:
        if(i > ranges[pt]):
            pt+=1
        if X[peak[pt]] < X[index]:
            peak[pt] = index
        index+=1
    for i in range(len(peak)):
        peak[i] = peak[i] - (peak[i]%fuz_fac[i])
        # peak[i] = peak[i] 
    return peak


def find_peak_fq(audio_path):

    x, sr = librosa.load(audio_path,sr=44100)


    X = librosa.stft(x,n_fft=8192)
    Xdb = (abs(X))
    X_t = X.transpose()
    Xdb_t = Xdb.transpose()
    all_peaks = []


    for time in range(Xdb_t.shape[0]):
        peak = find_pe(Xdb_t[time],8192,sr)
        all_peaks.append(peak)

    print("done")

    return  all_peaks

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
        json_out["song"] = find_song(temp_input_path,"audio")
        print(json_out)
        default_storage.delete(input_path)

        # example output
        # {'status': 'success', 'song': {'song_id': 0, 'song_file': './media/songs/song4.wav', 'singer': 'me', 'song_name': ' Force Projection | Cyberpunk 2077', 'link': 'bSpQpImpZbw', 'time': 54}}
        return JsonResponse(json_out) #SEND TO FRONTEND
    