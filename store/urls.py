from django.urls import path

from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url, include



urlpatterns = [

    path('', views.store_detail, name = "store_detail"),
    path("<int:uid>/<int:sid>/", views.user_store_detail, name = "user_store_detail"),
    path('create-auction/', views.create_auction, name='create_auction'),
    path('approve-applicant/', views.approve_applicant, name='approve_applicant'),
    path('decline-applicant/', views.decline_applicant, name='decline_applicant'),
    path('purchase/', views.purchase, name='purchase'),
    path('apply/', views.apply, name='apply'),
    path('activity/', views.activity, name='activity'),
    path('rankings/', views.rankings, name='rankings'),
    path('liveauctions/', views.liveauctions, name='liveauctions'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)