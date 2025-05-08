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
import librosa

# Create your views here.

def find_hash(path):
    peaks = find_peak_fq(path)

    length = len(peaks)
    hashes = []
    print(peaks[0:5])
    print(peaks[10],"peak len ",length)

    # for i in range(length-10):
    #     for col in range(len(peaks[i])):
    #         num_added = 0
    #         for j in range(0,10):
    #             for col_nex in range(len(peaks[i+j])):
    #                 if j==0 and col==col_nex:
    #                     continue

    #                 str_fq = str(peaks[i][col]) 
    #                 str_fq += str(peaks[i+j][col_nex])
    #                 str_fq += str(j)
    #                 # gen_hash = to_int(xxhash.xxh3_64_hexdigest(str_fq))
    #                 gen_hash = peaks[i][col]*1000000 + peaks[i+j][col_nex]*1000 + j
    #                 hashes.append((gen_hash,i))
    #                 num_added+=1

    #                 if num_added>3:
    #                     break

    #             if num_added>3:
    #                 break

    
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
        # str_fq = str(peaks[index][i] + (peaks[index][j]<<10)+(peaks[index][k]<<20))
        

    print("before hash len ",len(hashes))

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

    for song_path in audio_clips:

        new_song = song(song_id=song_id,song_file=audio_fpath+song_path,singer="me",song_name="me to")
        new_song.save()
        add_to_db(audio_fpath+song_path,new_song)
        song_id+=1
           
    print("hi"*10)
    return HttpResponse("done bro")

def to_int(st):
    return int(st[8:], 16)

def test(request):
    # new = song()
    # new.song_id = 5
    # new.song_file = "media/user/royalty-free-use-lofi-chill-background-music-dreamscape-201679.wav"
    # new.singer = "xy"
    # new.song_name = "xyz"
    # new.save()
    # new = fingerprint(hash=hsh,offset=0,song_id=new_song)
    # new.save()
    return HttpResponse("done bro")

def find_song(path):
    hashs = find_hash("./media/user/"+path)
    hash_dict = make_dict(hashs)
    hash_set = [hsh for hsh,off in hashs]
    str_hash = str(hash_set)
    str_hash = str_hash[1:-1]

#     query = """
#     SELECT count(*) as cnt,song_id_id 
#     FROM test.application_fingerprint 
#     WHERE hash in ( %s ) 
#     group by song_id_id
#     order by count(*) desc;
# """ % str_hash
    top_song = {}

    print("total hsh", len(hashs))
    for song_id in range(4):
        query = """
            SELECT hash, offset
            FROM test.application_fingerprint 
            WHERE hash in ( %s ) and song_id_id = %s order by offset;
        """ % (str_hash,song_id)

        matched_hsh = execute_raw_sql(query)

        length = len(matched_hsh)
        coherence_score=0
        print(matched_hsh[0:10])
        sum_offset = 0
        temp_off = []
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
                        if u_off1<u_off2 and abs(dif_offeset-(u_off2-u_off1))<5:
                            coherence_score+=1
                            sum_offset+= off1
                            mini_off = min(mini_off,off1)
                            temp_off.append(off1)
                            flag = False
                            break
                    if flag==False:
                        break

                # if abs(dif_offeset - SmallestDifference(user_off1,user_off2))<3:
                #     coherence_score+=1

        song_time = -1
        if not coherence_score == 0:
            song_time = sum_offset/coherence_score - len(hashs)/2

        print(temp_off)
        top_song[song_id] = (coherence_score,song_time*0.0463)

    

    print(top_song)
    return top_song

def idk(request):
    paths = ["song1_c.wav","song1_m.wav","song1_wec.wav","song1_ml.wav","song1_mll.wav","song1.wav","song2_sc.wav","song2_m.wav","song4_ml.wav","song4_webc.wav"]
    temp = {}
    for path in paths:
        print(path,".............")
        top_song = (find_song(path))
        # top_song[song] =

        temp[path] = top_song
        print("top song" ,top_song)
    print(temp)
    return render(request, 'temp.html',{"songs":temp})

def _delete_file(path):
    # Deletes file from filesystem.
    if os.path.isfile(path):
        os.remove(path)

def my_view(request):
    print(f"Great! You're using Python 3.6+. If you fail here, use the right version.")
    message = 'Upload as many files as you want!'
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = user_file(docfile=request.FILES['docfile'])
            newdoc.save()
            print("good\n"*10)

            # Redirect to the document list after POST
            return redirect('my-view')
        else:
            message = 'The form is not valid. Fix the following error:'
    else:
        form = DocumentForm()  # An empty, unbound form

    # Load documents for the list page
    # documents = Document.objects.all()

    # Render list page with the documents and the form
    context = {'form': form, 'message': message}
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
        # # time =150
        # peaks, _ = find_peaks(Xdb_t[time], prominence=1 ,width=1)
        # # if time == 150:
        # #     plt.figure(figsize=(14, 5))
        # #     plt.plot(peaks, Xdb_t[time][peaks] , "ob")
        # #     plt.plot(Xdb_t[time])
        # #     plt.show()
        # num_peaks = 6
        # heights = [Xdb_t[time,i] for i in peaks]
        # sorted_a = [peaks[i] for i in np.argsort(heights)]

        # # librosa.display.specshow(Xdb, sr=sr, x_axis='time', y_axis='hz')

        # heights = [Xdb_t[time,i] for i in peaks]
        # sorted_a = [peaks[i] for i in np.argsort(heights)]

        # if(len(sorted_a)>3):
        #     sorted_a = sorted_a[-3:]

        all_peaks.append(peak)

    print("done")

    return  all_peaks

@csrf_exempt
def upload_audio(request):
    if request.method == 'POST' and request.FILES.get('audio'):
        audio_file = request.FILES['audio']

        # Save original webm
        temp_input_path = default_storage.save('temp_input.wav', audio_file)
        input_path = os.path.join(settings.MEDIA_ROOT, temp_input_path)
        #print("temp:",temp_input_path, "\ninp:",input_path)

        # DO PROCESSING 

        # Clean up temp file
        # default_storage.delete(temp_input_path)

        return JsonResponse({'status': 'success'}) #SEND TO FRONTEND