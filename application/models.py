from django.db import models

# Create your models here.
class song(models.Model):
    song_id = models.SmallIntegerField(primary_key = True)
    song_file = models.FileField(null=True)
    singer = models.CharField(max_length=40,null=True)
    song_name = models.CharField(max_length=40,null=True)

    def __str__(self):
        return self.song_name

class fingerprint(models.Model):
    hash = models.IntegerField(primary_key=True,
        unique=False,
        default=None,
        )
    song_id = models.ForeignKey(song, on_delete=models.CASCADE)
    offset = models.SmallIntegerField()

    def __str__(self):
        return str(self.hash)


class user_file(models.Model):
    docfile = models.FileField(upload_to='temp')