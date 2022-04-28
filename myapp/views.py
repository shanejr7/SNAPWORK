from django.contrib.auth.models import User
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.utils.html import strip_tags
from store.models import Store
from store.models import User
from store.models import Follow
from store.models import Follower
from django.utils.html import strip_tags
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.validators import RegexValidator
from django.views.decorators.csrf import requires_csrf_token
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import update_last_login
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout
from django.utils import timezone
import datetime
import logging
import boto3
from botocore.exceptions import ClientError
import os
from django.conf import settings


s3_client = boto3.client('s3', region_name=settings.AWS_S3_REGION_NAME , aws_access_key_id=settings.AWS_ACCESS_KEY_ID ,
                               aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

# Create your views here.
def signup(request):

	query =request.POST.get("submit_signup")
	if query:
		valid = True
		email = "n/a"
		error = {}
		check_email = []
		check_username = []


		user_name = strip_tags(request.POST['name'])

		if request.POST['email']:
			email = request.POST['email']

		try:
			val = validate_email(email)
		except ValidationError as e:
			valid = False
			error = {'1':'invalid email'}
		
		
		username = strip_tags(request.POST['username'])
		phone_number = strip_tags(request.POST['phone'])
		password = strip_tags(request.POST['password'])
		re_password = strip_tags(request.POST['re-password'])

		if str(password) != str(re_password):
			valid = False
			error = {'2':password}
			error = {'2':re_password}

		try:
			check_email = User.objects.get(email__iexact=email)
			error = {'3':'email exists'}
		except:
			error = {}

		try:
			check_username = User.objects.get(username__iexact=username)
			error = {'4':'username exists'}
		except:
			error = {}
			


		if check_email:
			valid = False
			error = {'5':'email already exists'}

		if check_username:
			valid = False
			error = {'6':'username already exists'}

		date = datetime.datetime.now()
		time_stamp = date.strftime('%m-%d-%Y %H:%M')

		
		if user_name == None or email == None or username == None or phone_number == None or password == None or valid == False :
			error = {'7':'missing input'}
			errors = {

	        "error": error,

	    	}

			return render(request,'signup.html',errors)

		if user_name != None and email != None and username != None and phone_number != None and password != None and valid == True :
			# Create user and save to the database
			max_id = User.objects.last().id
			max_id = max_id +1
			create_user = User.create_user(self=User.objects,id=max_id,user_name=user_name,username=username,email=email,password=password,phone=phone_number,license="n/a",img_license_front_url="n/a",img_license_back_url="n/a", img_url="images/author/user.jpg",background_img_url="images/background/subheader.jpg",verified_identity=False,background_check_status ="n/a",quality_rank =0.0, timestamp=time_stamp)
			create_user.save()
			create_user.last_login = timezone.now()
			create_user.save(update_fields=['last_login'])

			request.session['id'] = max_id;
			request.session['username'] = username;
			request.session['email'] = email;
			request.session['img_url'] = 'images/author/user.jpg';
			request.session['quality_rank'] = 0.0;

			return redirect('/myapp/myprofile')
	return render(request,'signup.html')



def login(request):
	error = {}
	query =request.POST.get("submit_login")
	user = ""
	if query:
		username = request.POST['username']
		password = request.POST['password']
		try:
			user = User.objects.get(username__iexact=username)
		except:
			error = {'1':'invalid credentials'}

			errors = {

	        "error": error,

	    	}
			return render(request,'login.html',errors)
		

		# user = authenticate(request,username=username,password=password)
		if user is not None and str(password) == str(user.password):
			user.last_login = timezone.now()
			user.save(update_fields=['last_login'])
			# auth_login(request,user)
			user = User.objects.get(username=username)
			request.session['id'] = user.id
			request.session['username'] = user.username
			request.session['email'] = user.email
			request.session['img_url'] = user.img_url;
			request.session['quality_rank'] = user.quality_rank
			return redirect('/myapp/myprofile')
		else:
			error = {'1':'invalid credentials'}

			errors = {

	        "error": error,

	    	}

			return render(request,'login.html',errors)


	return render(request,'login.html')


def logout_request(request):

	del request.session['id'];
	del request.session['username'];
	del request.session['email'];
	del request.session['img_url'];
	del request.session['quality_rank'];
	logout(request)

	return redirect('/myapp/login')


def profile_auth(request):

	owner_obj = []
	store_obj = []
	follow_session_obj = []
	error = []

	try:
		if not request.session['id']:
			return redirect('/myapp/login')
		else:
			uid = request.session['id']
			owner_obj = User.objects.get(pk=uid)
			store_obj = Store.objects.filter(user_id=owner_obj.id)
			follow_obj = Follow.objects.filter(user_follower_id=owner_obj.id).values('user__id','user__username','user__email','user__img_url','user__timestamp')
			follower_obj = Follow.objects.filter(user_id=owner_obj.id).values('user__id','user__username','user__email','user__img_url','user__timestamp')
			context = {
        		"products": store_obj,
        		"user": owner_obj,
        		"follow_tracker":follow_obj,
        		"follower_tracker":follower_obj,
        		"error": error,

    		}

			return render(request,'myprofile.html',context)
	except:
		return redirect('/myapp/login')


def profile_create_auth(request):
	return render(request,'create.html')

def profile_wallet_auth(request):
	return render(request,'wallet.html')

@requires_csrf_token
def edit_profile_auth(request):

	error = {}
	query =request.POST.get("submit_update_profile")

	if query:

		user_id = request.POST['user_id']
		upload_profile_img = request.FILES['upload_profile_img']
		# upload_banner_img = request.FILES['upload_banner_img']
		key_profile_img = "images/author/"+ str(upload_profile_img)
		# key_banner_img = "images/background/"+ str(upload_profile_img)
		file_name = upload_profile_img

		#try : only when profile image is changed
		#Upload a file to an S3 bucket

    	#:param file_name: File to upload
    	#:param bucket: Bucket to upload to
    	#:param object_name: S3 object name. If not specified then file_name is used
    	#:return: True if file was uploaded, else False

    	# If S3 object_name was not specified, use file_name

		#Upload statments

		if upload_profile_img:
	
			try:
				user = User.objects.get(id=user_id)
				s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME,Key=user.img_url)
				user.img_url = key_profile_img;
				response = s3_client.upload_fileobj(file_name, settings.AWS_STORAGE_BUCKET_NAME, key_profile_img)
				user.save()
				request.session['img_url'] = user.img_url
				return render(request,'editprofile.html')
			except ClientError as e:
				error = {'1':"images was not uploaded succesfully"}
				context = {
        			"error": error,
    			}
				return render(request,'editprofile.html',context)
				logging.error(e)
				return False
			return True


		#try : only when background images is changed
		# try:
		# 	response = s3_client.upload_fileobj(file_name, settings.AWS_STORAGE_BUCKET_NAME, key_banner_img )
		# 	# s3.Object(settings.AWS_STORAGE_BUCKET_NAME, 'images/author/file_name').delete() # old path 
		# 	return render(request,'editprofile.html')
		# except ClientError as e:
		# 	error = {'1':"images was not uploaded succesfully"}
		# 	context = {
  #       		"error": error,
  #   		}
		# 	return render(request,'editprofile.html',context)
		# 	logging.error(e)
		# 	return False
		# return True



		#try : only when profile and background image is changed

		# remove old path from amazon storage and database
		# store new path in database and store images amazon storage

		


	context = {
        "error": error,
    }

	return render(request,'editprofile.html',context)

def profile(request,uid):

	owner_obj = []
	store_obj = []
	follow_session_obj = []
	follow_obj = []
	follower_obj = []
	session_id = None
	isFollow = False
	error = []

	uid = strip_tags(uid)


	try:
		session_id = request.session['id']
	except:
		redirect 

 
	if int(uid):
		owner_obj = User.objects.get(pk=uid)
		store_obj = Store.objects.filter(user_id=owner_obj.id)
	
		try:
			follower_obj = Follower.objects.filter(user_follower_id=owner_obj.id).values('user__id','user__username','user__email','user__img_url','user__timestamp')
			follow_obj = Follow.objects.filter(user_follower_id=owner_obj.id).values('user__id','user__username','user__email','user__img_url','user__timestamp')
			follow_session_obj = Follow.objects.filter(user_id=owner_obj.id, user_follower_id =session_id).values('user__id','user__username','user__email','user__img_url','user__timestamp')
		except Follow.DoesNotExist:
			follow_session_obj = []
			follow_obj = []
			follower_obj = []

			
	else:
		error = "This page is empty. Please come back soon."


	if request.POST:

		if follow_session_obj:
			Follower.objects.filter(user_follower_id=owner_obj.id).delete()
			Follow.objects.filter(user_follower_id=session_id).delete()

		else:
			follow_session_obj = Follow(user_id=owner_obj.id, user_follower_id =session_id)
			follow_session_obj.save()

			follower = Follower(user_id=session_id, user_follower_id =owner_obj.id)
			follower.save()
			follower_obj = Follower.objects.filter(user_follower_id=owner_obj.id).values('user__id','user__username','user__email','user__img_url','user__timestamp')
			follow_obj = Follow.objects.filter(user_follower_id=owner_obj.id).values('user__id','user__username','user__email','user__img_url','user__timestamp')
			follow_session_obj = Follow.objects.filter(user_id=owner_obj.id, user_follower_id =session_id).values('user__id','user__username','user__email','user__img_url','user__timestamp')
		

	if Follow.objects.filter(user_id=owner_obj.id, user_follower_id =session_id).exists():
		isFollow = True
	else:
		isFollow = False

	context = {

        "products": store_obj,
        "user": owner_obj,
        "session_follower":follow_session_obj,
        "follow_tracker":follow_obj,
        "follower_tracker":follower_obj,
        "isFollow": isFollow,
        "error": error,

    }
	return render(request,'profile.html',context)


def create_auth(request):
	return render(request,'create.html')



