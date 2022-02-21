from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound

# Create your views here.
def custom_404(request, exception):
    if exception:
        return HttpResponseNotFound('<h1>Page not found</h1>')
