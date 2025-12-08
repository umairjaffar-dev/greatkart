from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def category(request):
    return HttpResponse("This is category app.")
