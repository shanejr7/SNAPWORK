from django.contrib import admin
from django.contrib.auth.models import UserManager
from .models import User, Store, Auction, Stakeholder, Stage, Follow, Like

# Register your models here.
admin.site.register(User)

admin.site.register(Store)

admin.site.register(Auction)

admin.site.register(Stakeholder)

admin.site.register(Stage)

admin.site.register(Follow)

admin.site.register(Like)
