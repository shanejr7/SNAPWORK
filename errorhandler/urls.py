from django.urls import path
from . import views 
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url, include


#UrlConf
handler404 = 'errorhandler.views.custom_404'

urlpatterns = [

	path(handler404, views.custom_404, name= "404")
	
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)