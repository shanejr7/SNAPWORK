from django.contrib.auth.models import User
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.utils.html import strip_tags
from store.models import Store
from store.models import User
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


# Create your views here.
def signup(request):

	query =request.POST.get("submit_signup")
	if query:
		valid = True
		email = "n/a"
		user_name = strip_tags(request.POST['name'])
		if request.POST['email']:
			email = request.POST['email']
		error = {}
		check_email = []
		check_username = []

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
			# error = {'7':'missing input'}
			errors = {

	        "error": error,

	    	}

			return render(request,'signup.html',errors)

		if user_name != None and email != None and username != None and phone_number != None and password != None and valid == True :
			# Create user and save to the database
			max_id = User.objects.last().id
			max_id = max_id +1
			create_user = User.create_user(self=User.objects,id=max_id,user_name=user_name,username=username,email=email,password=password,phone=phone_number,license="n/a",img_license_front_url="n/a",img_license_back_url="n/a", img_url="n/a",background_img_url="n/a",verified_identity=False,background_check_status ="n/a",quality_rank =0.0, timestamp=time_stamp)
			create_user.save()
			create_user.last_login = timezone.now()
			create_user.save(update_fields=['last_login'])

			request.session['id'] = max_id;
			request.session['username'] = username;
			request.session['email'] = email;
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
	del request.session['quality_rank'];
	logout(request)

	return redirect('/myapp/login')


def profile_auth(request):
	return render(request,'myprofile.html')

def edit_profile_auth(request):
	return render(request,'editprofile.html')

def profile(request,uid):

	owner_obj = []
	store_obj = []
	error = []

	uid = strip_tags(uid)
 
	if int(uid):
		owner_obj = User.objects.get(pk=uid)
		store_obj = Store.objects.filter(user_id=owner_obj.id)
 
	else:
		error = "This page is empty. Please come back soon."

	context = {

        "products": store_obj,
        "user": owner_obj,
        "error": error,

    }
	return render(request,'profile.html',context)


def create_auth(request):
	return render(request,'create.html')



