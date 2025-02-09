from django.db import models

# Create your models here.
class song(models.Model):
    song_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length= 40)
    singer = models.CharField(max_length=40,default='null')
    image = models.ImageField(upload_to='images',null=True)
    song = models.FileField(upload_to='images',null=True)

    def __str__(self):
        return self.title