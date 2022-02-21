from django.shortcuts import render

# Create your views here.
def tag():
	return render(request, "tags.html", context)