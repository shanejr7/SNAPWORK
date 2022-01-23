from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def main(request):
	return render(request,'hello.html',{'name' :'Shane'})

# def main(request):
# 	return render(request,'login.html',{'name' :'Shane'})

# def main(request):
# 	return render(request,'signup.html',{'name' :'Shane'})

# def main(request):
# 	return render(request,'home.html',{'name' :'Shane'})