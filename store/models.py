from django.db import models
from django.contrib.auth.models import AbstractBaseUser, UserManager,BaseUserManager
from django.contrib.auth.hashers import make_password

# Create your models here.
from django.db import models



class User(AbstractBaseUser,BaseUserManager):

    user_name = models.TextField()

    username = models.TextField(null = True)

    email =  models.EmailField(unique=True)

    password = models.TextField(null = True)

    phone = models.TextField(default = "n/a")

    license = models.TextField()

    img_license_front_url = models.TextField(default = "n/a")
    
    img_license_back_url = models.TextField(default = "n/a")

    img_url = models.TextField(default = "n/a") 

    background_img_url = models.TextField(default = "n/a") 

    verified_identity = models.BooleanField(default = False)

    background_check_status = models.TextField(default = "n/a")

    quality_rank = models.FloatField(default = 0.0)

    timestamp = models.TextField()

    USERNAME_FIELD = 'email'

    objects = UserManager()

    def create_user(self,id,user_name,username,email,password,phone,license,img_license_front_url,img_license_back_url, img_url,background_img_url,verified_identity,background_check_status,quality_rank, timestamp):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            id = id,
            user_name =user_name,
            username = username,
            email=self.normalize_email(email),
            password=password,
            phone = phone,
            license = license,
            img_license_front_url =img_license_front_url,
            img_license_back_url =img_license_back_url,
            img_url =img_url,
            background_img_url=background_img_url,
            verified_identity = verified_identity,
            background_check_status = background_check_status,
            quality_rank = quality_rank,
            timestamp = timestamp,
        )

        user.save(using=self._db)
        return user

    def log_user(self,u):
        user = self.model(u.id)

        user.save(update_fields=['last_login'])
        return user

class Follow(models.Model):

    user_follower_id = models.IntegerField()

    timestamp = models.TextField(null = True)

    user = models.ForeignKey("User", on_delete=models.SET_NULL, null=True)

class Follower(models.Model):

    user_follower_id = models.IntegerField()

    timestamp = models.TextField(null = True)

    user = models.ForeignKey("User", on_delete=models.SET_NULL, null=True)


class Like(models.Model):

    user_id = models.IntegerField()

    timestamp = models.TextField()

    store = models.ForeignKey("Store", on_delete=models.SET_NULL, null=True)

class Store(models.Model):

    product = models.TextField()

    title = models.TextField()

    body = models.TextField()

    price = models.FloatField()

    minimum_bid = models.FloatField(null=True)

    quantity = models.IntegerField(null=True)

    auction = models.BooleanField(null = True)

    product_type = models.TextField(default = "n/a")

    contract_type = models.TextField(default = "n/a")

    service_type = models.TextField(default = "n/a")

    data_type = models.TextField(default = "n/a")

    season = models.TextField(default = "n/a")

    views = models.IntegerField(default=0)

    img_url = models.TextField(default = "n/a")

    address = models.TextField(default = "n/a")

    address_2 = models.TextField(default = "n/a")

    city = models.TextField(default = "n/a")

    zip_code = models.TextField(default = "n/a")

    state = models.TextField(default = "n/a")

    country = models.TextField(default = "n/a")

    dob = models.TextField(default = "n/a")

    duration_start_timestamp = models.TextField(default = "n/a")

    duration_timestamp = models.TextField(default = "n/a")

    timestamp = models.TextField()

    user = models.ForeignKey("User", on_delete=models.SET_NULL, null=True)


class Auction(models.Model):

    highest_bid = models.BooleanField(null = True)

    accepted_bid = models.BooleanField(null = True)

    application = models.BooleanField(null = True)

    price = models.IntegerField()

    quantity = models.IntegerField(null=True)

    timestamp = models.TextField()

    store = models.ForeignKey("Store", on_delete=models.SET_NULL, related_name='+', null=True)
    user = models.ForeignKey("User", on_delete=models.SET_NULL, null=True)

class Stakeholder(models.Model):

    price = models.IntegerField()

    quantity = models.IntegerField(null=True)

    timestamp = models.TextField()

    store = models.ForeignKey("Store", on_delete=models.SET_NULL, related_name='+', null=True)
    user = models.ForeignKey("User", on_delete=models.SET_NULL,null=True)

class Stage(models.Model):

    continuation_timestamp = models.TextField()

    termination_timestamp = models.TextField()

    img_url = models.TextField(default = "n/a")

    address = models.TextField(default = "n/a")

    timestamp = models.TextField()

    stakeholder = models.ForeignKey("Stakeholder", on_delete=models.SET_NULL, related_name='+', null=True)
    user = models.ForeignKey("User", on_delete=models.SET_NULL,  null=True)

class Order(models.Model):

    product = models.TextField()

    title = models.TextField()

    body = models.TextField()

    price = models.IntegerField()

    quantity = models.IntegerField(null=True)

    auction = models.BooleanField(null = True)

    season = models.TextField(default = "n/a")

    img_url = models.TextField(default = "n/a")

    address = models.TextField(default = "n/a")

    address_2 = models.TextField(default = "n/a")

    city = models.TextField(default = "n/a")

    zip_code = models.TextField(default = "n/a")

    state = models.TextField(default = "n/a")

    country = models.TextField(default = "n/a")

    timestamp = models.TextField()

    user = models.ForeignKey("User", on_delete=models.SET_NULL, null=True)
    store = models.ForeignKey("Store", on_delete=models.SET_NULL, null=True)



