from django.shortcuts import render
from django.http import HttpResponse
from .models import song

# Create your views here.

def say_hello(request):
    

    return render(request,'index.html')

def idk(request):
    return HttpResponse("hi bro")