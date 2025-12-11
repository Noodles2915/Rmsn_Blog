from django.shortcuts import render,redirect
from users import views

def index(request):
    return render(request, 'index.html')