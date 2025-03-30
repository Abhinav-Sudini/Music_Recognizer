from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import song,user_file,fingerprint
from .form import DocumentForm
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
from itertools import islice
#for loading and visualizing audio files
from django.db import connection
from queue import Queue
import xxhash
import numpy as np
import librosa
import os

# Create your views here.

def find_hash(path):
    peaks = find_peak_fq(path)

    length = len(peaks)
    hashes = []
    print(peaks[10],"peak len ",length)

    # for i in range(length-10):
    #     for col in range(len(peaks[0])-1):
    #         for j in range(1,10):
    #            for col_nex in range(len(peaks[0])-1):
    #                 str_fq = str(peaks[i][col]) 
    #                 str_fq += str(peaks[i+j][col_nex])
    #                 str_fq += str(j)
    #                 gen_hash = to_int(xxhash.xxh3_64_hexdigest(str_fq))
    #                 hashes.append(gen_hash)


    
    for index in range(length):
        pt = 0
        temp = []
        fuz_fac = [1,2,3,5,10,20,35,50,60]
        for k in peaks[index]:
            temp.append((k))
            pt+=1
        
        str_fq = str(sorted(list(temp[:-1])))
        gen_hash = to_int(xxhash.xxh3_64_hexdigest(str_fq))
        hashes.append(gen_hash)
        # str_fq = str(peaks[index][i] + (peaks[index][j]<<10)+(peaks[index][k]<<20))
        

    print("before hash len ",len(hashes))

    return hashes

def add_to_db(path,new_song):

    hashes = find_hash(path)
    hashset = hashes
    print("need to add ",len(hashset))
    batch_size = 500
    objs = (fingerprint(hash=hsh,offset=0,song_id=new_song) for hsh in hashset)
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
    hash_set = find_hash("./media/user/"+path)
    str_hash = str(hash_set)
    str_hash = str_hash[1:-1]

    query = """
    SELECT count(*),song_id_id 
    FROM test.application_fingerprint 
    WHERE hash in ( %s ) 
    group by song_id_id
    order by count(*) limit 5;
""" % str_hash

    with connection.cursor() as cursor:
        cursor.execute(query)
        print(cursor.fetchall())

def idk(request):
    paths = ["song1_c.wav","song1_m.wav","song1_ml.wav","song1_mll.wav","song2_sc.wav","song2_m.wav","song3_m.wav","song4_ml.wav"]

    for path in paths:
        print(path,".............")
        find_song(path)
    
    return HttpResponse("hi bro")

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
    ranges = [20,40,80,120,180,300,800,2000,2000000]
    fuz_fac = [2,2,3,3,3,4,4,4,4,5,5,5,10]
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