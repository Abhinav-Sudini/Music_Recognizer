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

def find_song(path,type="file"):
    hashs = find_hash("./media/"+path)
    hash_dict = make_dict(hashs)
    hash_set = [hsh for hsh,off in hashs]
    str_hash = str(hash_set)
    str_hash = str_hash[1:-1]
    top_song = {}

