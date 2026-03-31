import librosa
import xxhash

from .functions import *

def find_hash(path):
    peaks = find_peak_fq(path)

    length = len(peaks)
    hashes = []
    for index in range(length):
        pt = 0
        temp = []
        
        str_fq = str(sorted(list(temp[:-1])))
        
        gen_hash = to_int(xxhash.xxh3_64_hexdigest(str_fq))
        hashes.append((gen_hash,index))

    return hashes


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
        # peak[i] = peak[i] - (peak[i]%fuz_fac[i])
        peak[i] = peak[i] 
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

