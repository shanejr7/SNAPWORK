from django.contrib.auth.models import User
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.utils.html import strip_tags
from store.models import Store
from store.models import User
from store.models import Follow
from store.models import Follower
from store.models import Like
from store.models import Auction
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
			max_id = 0
			try:
				max_id = User.objects.last().id
				max_id = max_id +1
			except:
				max_id = 1

			create_user = User.create_user(self=User.objects,id=max_id,user_name=user_name,username=username,email=email,password=password,phone=phone_number,license="n/a",img_license_front_url="n/a",img_license_back_url="n/a", img_url="n/a",background_img_url="n/a",verified_identity=False,background_check_status ="n/a",quality_rank =0.0, timestamp=time_stamp)
			create_user.save()
			create_user.last_login = timezone.now()
			create_user.save(update_fields=['last_login'])

			request.session['id'] = max_id;
			request.session['username'] = username;
			request.session['email'] = email;
			request.session['img_url'] = 'n/a';
			request.session['background_img_url'] = 'n/a'
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

			if user.img_url != 'n/a':
				key_profile_img = str(user.img_url)
				request.session['img_url']  = s3_client.generate_presigned_url('get_object',
                                Params={
                                    'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                    'Key': key_profile_img,
                                },                                  
                                ExpiresIn=3600)
			else:
				request.session['img_url'] = user.img_url;

			if user.background_img_url != 'n/a':
				key_banner_img  = str(user.background_img_url)
				request.session['background_img_url']  = s3_client.generate_presigned_url('get_object',
                                Params={
                                    'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                    'Key': key_banner_img ,
                                },                                  
                                ExpiresIn=3600)
			else:
				request.session['background_img_url'] = user.background_img_url;

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

	del request.session['id']
	del request.session['username']
	del request.session['email']
	del request.session['img_url']
	del request.session['background_img_url']
	del request.session['quality_rank']
	logout(request)

	return redirect('/myapp/login')


def profile_auth(request):

	owner_obj = []
	store_obj = []
	store_obj_likes = []
	jobs = []
	applications = []
	orders = []
	follow_session_obj = []
	error = []

	try:
		if not request.session['id']:
			return redirect('/myapp/login')
		else:
			uid = request.session['id']
			owner_obj = User.objects.get(pk=uid)
			store_obj = Store.objects.filter(user_id=owner_obj.id)
			#jobs
			#applications
			applications = Auction.objects.filter(user_id=uid).values('user__id','user__username','user__email','user__license','user__timestamp',
        'store__id','store__product','store__title','store__body','store__price','store__quantity','store__auction','store__product_type', 'store__contract_type','store__service_type',
        'store__data_type','store__season','store__views','store__img_url','store__address', 'store__duration_timestamp','store__timestamp').order_by('user__timestamp') 
			#likes
			follower_obj = Follower.objects.filter(user_follower_id=owner_obj.id).values('user__id','user__username','user__email','user__img_url','user__timestamp')
			follow_obj = Follow.objects.filter(user_follower_id=owner_obj.id).values('user__id','user__username','user__email','user__img_url','user__timestamp')
		
			for store in store_obj:
				store.img_url = s3_client.generate_presigned_url('get_object',
                                Params={
                                    'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                    'Key': str(store.img_url),
                                })

			if follow_obj:
				for follow in follow_obj:
					if follow['user__img_url'] !='n/a':
						key_profile_img = str(follow['user__img_url'])
						follow['user__img_url'] = s3_client.generate_presigned_url('get_object',
                                Params={
                                    'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                    'Key': key_profile_img,
                                },                                  
                                ExpiresIn=3600)

			if follower_obj:
				for follower in follower_obj:
					if follower['user__img_url'] !='n/a':
						key_profile_img = str(follower['user__img_url'])
						follower['user__img_url'] = s3_client.generate_presigned_url('get_object',
                                Params={
                                    'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                    'Key': key_profile_img,
                                },                                  
                                ExpiresIn=3600)

			context = {
        		"products": store_obj,
        		"user": owner_obj,
        		"applications": applications,
        		"follow_tracker":follow_obj,
        		"follower_tracker":follower_obj,
        		"error": error,

    		}

			return render(request,'myprofile.html',context)
	except:
		return redirect('/myapp/login')

@requires_csrf_token
def profile_create_auth(request):

	error = []
	success = []

	# validate authorize user route request
	try:
		if request.session['id']:
			pass
	except:
		return redirect('/myapp/login')


	# REQUEST item UPLOAD

	query = request.POST.get('create_item')

	if query:
		user_id = request.session['id'] # generate user store on successful upload
		valid = True

		product = ''
		title = ''
		body =  ''
		price = 0.0
		minimum_bid = 0.0
		quantity = ''
		auction =  request.POST.get('item_bid', False)

		if auction == 'on':
			auction == True
		else:
			auction == False

		season = ''
		upload_img =''
		file_name =''
		key_img =''
		address= ''
		address_2 = ''
		city = ''
		state = ''
		country = ''
		zip_code = ''

		#input validator 
		if request.POST['item_type']:
			product = request.POST['item_title']
		else:
			error= {'1':'missing item type'}
			valid = False

		if request.POST['item_title']:
				title = request.POST['item_title']
		else:
			error= {'2':'missing title'}
			valid = False

		if request.POST['item_desc']:
				body =  request.POST['item_desc']
		else:
			error= {'3':'missing description'}
			valid = False

		if request.POST['item_price']: # float value 
				price = request.POST['item_price']
				price = float(price)
		else:
			error= {'4':'missing price'}
			valid = False


		if request.POST['item_quantity']: # integer value
				quantity = request.POST['item_quantity']
		else:
			error= {'5':'missing quantity'}
			valid = False

		if request.POST['item_season']:
				season = request.POST['item_season']
		else:
			error= {'6':'missing seasons'}
			valid = False

		
		if request.FILES['upload_file']: # valid for .PNG, .JPG, .GIF, .WEBP or .MP4
			upload_img = request.FILES['upload_file']
			file_name = upload_img
			key_img = "images/items/"+str(user_id)+ str(upload_img)
		else:
			error= {'7':'missing image'}
			valid = False

		if request.POST['item_address']:
			address = request.POST['item_address']
		else:
			error = {'8': 'missing address'}
			valid = False

		if request.POST['item_address_2']:
			address_2 = request.POST['item_address_2']

		if request.POST['item_city']:
			city =request.POST['item_city']
		else:
			error = {'9': 'missing city'}
			valid = False

		if request.POST['item_state']:
			state = request.POST['item_state']
		else:
			error = {'10': 'missing state'}
			valid = False
		if request.POST['item_country']:
			country = request.POST['item_country']
		else:
			error = {'11': 'missing country'}
			valid = False

		if request.POST['item_zip_code']:
			zip_code = request.POST['item_zip_code']
		else:
			error = {'12': 'missing zip code'}
			valid = False


		if valid == True:

			product_type = 'n/a'
			contract_type = 'n/a'
			service_type = 'n/a'
			data_type = 'n/a'
			dob = 'n/a'
			duration_start_timestamp = 'n/a'
			duration_timestamp = 'n/a'


			if request.POST['item_type'] == 'Product':
				product_type = 'product'
			elif request.POST['item_type'] == 'Contract':
				contract_type = 'contract'
				if request.POST['starting_date_contract']:
					duration_start_timestamp = request.POST['starting_date_contract']
				else:
					error= {'13':'missing start date'}
					valid = False
				if request.POST['expiration_date_contract']:
					duration_timestamp = request.POST['expiration_date_contract']
				else:
					error= {'14':'missing expiration date'}
					valid = False
				if request.POST['item_price_bid']: # integer value 
					minimum_bid = request.POST['item_price_bid']
					minimum_bid = float(minimum_bid)
				else:
					error= {'15':'missing minimum bid'}
					valid = False
			elif request.POST['item_type'] == 'Service':
				service_type = 'service'
				dob = request.POST['item_birth_date']
				if request.POST['starting_date_service']:
					duration_start_timestamp = request.POST['starting_date_service']
				else:
					error= {'16':'missing start date'}
					valid = False
				if request.POST['expiration_date_service']:
					duration_timestamp = request.POST['expiration_date_service']
				else:
					error= {'17':'missing expiration date'}
					valid = False
			elif request.POST['item_type'] == 'Content':
				data_type = 'Data'
				dob = request.POST['item_birth_date']

			if valid == True:
				user = User.objects.get(id=user_id)
				date = datetime.datetime.now()

				time_stamp = date.strftime('%m/%d/%Y %H:%M')
	
				if duration_timestamp != 'n/a':
					year = duration_timestamp[0:4]
					month = duration_timestamp[5:7]
					day = duration_timestamp[8:10]
					duration_timestamp = month +'/' +day +'/'+year + ' 12:00'

				if duration_start_timestamp  != 'n/a':
					year = duration_start_timestamp[0:4]
					month = duration_start_timestamp[5:7]
					day = duration_start_timestamp[8:10]
					duration_start_timestamp = month +'/' +day +'/'+year + ' 12:00' 
				

				store = Store(product=product,title=title,body=body, price=price,minimum_bid=minimum_bid,quantity=quantity,
				auction=auction,product_type=product_type,contract_type=contract_type,
				service_type= service_type,data_type =data_type ,season =season,img_url='',
				address=address,address_2=address_2,city=city,zip_code =zip_code,state =state,
				country=country,timestamp=time_stamp,duration_timestamp=duration_timestamp,
				duration_start_timestamp=duration_start_timestamp, user =user)

				store.img_url = key_img;
				response = s3_client.upload_fileobj(file_name, settings.AWS_STORAGE_BUCKET_NAME, key_img)
				store.save()	
				success = {"1":"success: snapwork item has been created!"}


	context = {
	"error": error,
	"success": success,
	}

	return render(request,'create.html',context)

def profile_wallet_auth(request):
	return render(request,'wallet.html')

@requires_csrf_token
def edit_profile_auth(request):

	try:
		if request.session['id']:
			pass
	except:
		return redirect('/myapp/login')

	error = {}
	query =request.POST.get("submit_update_profile")

	if query:

		upload_profile_img = ''
		upload_banner_img = ''
		key_profile_img =''
		key_banner_img =''

		user_id = request.POST['user_id']

		try:
			if request.FILES['upload_profile_img']:
				upload_profile_img = request.FILES['upload_profile_img']
				profile_file_name = upload_profile_img
				key_profile_img = "images/author/"+str(user_id)+ str(upload_profile_img)
		except:
			upload_profile_img = ''

		try:
			if request.FILES['upload_banner_img']:
				upload_banner_img = request.FILES['upload_banner_img']
				banner_file_name = upload_banner_img
				key_banner_img = "images/background/"+str(user_id)+ str(upload_banner_img )
		except:
			upload_banner_img = ''


		#try : only when profile image is changed
		#Upload a file to an S3 bucket

    	#:param file_name: File to upload
    	#:param bucket: Bucket to upload to
    	#:param object_name: S3 object name. If not specified then file_name is used
    	#:return: True if file was uploaded, else False

    	# If S3 object_name was not specified, use file_name

		#Upload statments

		if upload_profile_img != '' and upload_banner_img == '':
	
			try:
				user = User.objects.get(id=user_id)
				try:
					s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME,Key=user.img_url)
				except:
					user.img_url = key_profile_img;

				user.img_url = key_profile_img;
				response = s3_client.upload_fileobj(profile_file_name, settings.AWS_STORAGE_BUCKET_NAME, key_profile_img)
				user.save()
			
				request.session['img_url']  = s3_client.generate_presigned_url('get_object',
                                Params={
                                    'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                    'Key': key_profile_img,
                                })

				return render(request,'editprofile.html')
			except ClientError as e:
				error = {'1':"profile images was not uploaded succesfully"}
				context = {
        			"error": error,
    			}
				return render(request,'editprofile.html',context)
				logging.error(e)
				return False
			return True

		
		if upload_profile_img == '' and upload_banner_img != '':
	
			try:
				user = User.objects.get(id=user_id)
				try:
					s3_client.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME,Key=user.background_img_url)
				except:
					user.background_img_url = key_banner_img;
				user.background_img_url = key_banner_img;
				response = s3_client.upload_fileobj(banner_file_name, settings.AWS_STORAGE_BUCKET_NAME, key_banner_img)
				user.save()
			
				request.session['background_img_url']  = s3_client.generate_presigned_url('get_object',
                                Params={
                                    'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                    'Key': key_banner_img ,
                                })

				return render(request,'editprofile.html')
			except ClientError as e:
				error = {'1':"banner images was not uploaded succesfully"}
				context = {
        			"error": error,
    			}
				return render(request,'editprofile.html',context)
				logging.error(e)
				return False
			return True

		


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

		if owner_obj.img_url != 'n/a':
			owner_obj.img_url  = s3_client.generate_presigned_url('get_object',
                                Params={
                                    'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                    'Key': str(owner_obj.img_url),
                                })
		if owner_obj.background_img_url != 'n/a':
			owner_obj.background_img_url  = s3_client.generate_presigned_url('get_object',
                                Params={
                                    'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                    'Key': str(owner_obj.background_img_url),
                                })

		for store in store_obj:
			store.img_url  = s3_client.generate_presigned_url('get_object',
                                Params={
                                    'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                    'Key': str(store.img_url),
                                })

	
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
			Follower.objects.filter(user_follower_id=owner_obj.id,user_id=session_id).delete()
			Follow.objects.filter(user_follower_id=session_id,user_id=owner_obj.id).delete()

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

	if follow_obj:
		for follow in follow_obj:
			if follow['user__img_url'] !='n/a':
				key_profile_img = str(follow['user__img_url'])
				follow['user__img_url'] = s3_client.generate_presigned_url('get_object',
                                Params={
                                    'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                    'Key': key_profile_img,
                                },                                  
                                ExpiresIn=3600)

	if follower_obj:
		for follower in follower_obj:
			if follower['user__img_url'] !='n/a':
				key_profile_img = str(follower['user__img_url'])
				follower['user__img_url'] = s3_client.generate_presigned_url('get_object',
                                Params={
                                    'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                    'Key': key_profile_img,
                                },                                  
                                ExpiresIn=3600)
	


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

# @requires_csrf_token
# def create_auth(request):
# 	try:
# 		if not request.session['id']:
# 			return redirect('/myapp/login')
# 	except:
# 		return redirect('/myapp/login') 
# 			# return redirect('/myapp/login')


# 	return render(request,'create.html')



