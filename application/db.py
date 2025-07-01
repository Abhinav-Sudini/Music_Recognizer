from itertools import islice
import xxhash

from .functions import *
from .find_song import *
from .models import song,user_file,fingerprint

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