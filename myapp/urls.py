from django.urls import path
from . import views 

#UrlConf
urlpatterns = [
	path('hello/', views.main)
]