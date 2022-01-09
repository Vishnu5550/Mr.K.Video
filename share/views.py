from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
global usname

import random
# Create  views here.
def home(request):
	
	if not request.user.is_authenticated:
		demo_videos = VideoPost.objects.all().order_by('-id')
		eve=Event.objects.all()
		print(demo_videos)
		params = {'videos': demo_videos, 'Eventd':eve}
		return render(request, 'welcome.html', params)
	
	else:
		all_videos = VideoPost.objects.all().order_by('-id')
		eve=Event.objects.all()
		params = {'all_videos': all_videos, 'Eventd':eve}
		return render(request, 'home.html', params)
def adm(request):
	all_videos = VideoPost.objects.all().order_by('-id')
	valli=True
	print('hello')
	params = {'all_videos': all_videos,'vall':valli}	
	return render(request, 'home.html', params)
def eventreg(request):
	if request.method=='POST':
		title=request.POST['title']
		link=request.POST['link']
		eveimg=request.FILES['uploadFromPC']
		event=Event(imd=eveimg,detail=title,link=link)
		event.save()
		demo_videos = VideoPost.objects.all().order_by('-id')[:5]
		eve=Event.objects.all()
		for i in eve:
			print(i.detail)
			print(i.id)
		# params = {'videos': demo_videos, 'Eventd':eve}
		# return render(request, 'welcome.html', params)
		# all_videos = VideoPost.objects.all().order_by('-id')
		# params = {'all_videos': all_videos}
		# return render(request, 'home.html', params)
		return redirect('home')
	else:
		all_videos = VideoPost.objects.all().order_by('-id')
		params = {'all_videos': all_videos}
		return render(request, 'home.html', params)
def search(request):
	query = request.GET['search_query']
	try:
		user_obj = User.objects.filter(username__icontains=query)
	except:
		 user_obj = User.objects.none()	
	try:
		video_obj= VideoPost.objects.all()
		vi=[]
		for v in video_obj:
			# print(v.title)
			if(query in v.title):
				print(v)
				vi.append(v)
		print(video_obj)
		print(vi)
	except:
		video_obj=VideoPost.objects.none()
	params = {'user_obj': user_obj,'video_obj':vi}
	
	return render(request, 'search_page.html', params)

def upload_video(request):
	if request.method == 'POST':
		title = request.POST['title']
		desc = request.POST['desc']
		video_file = request.FILES['fileName']
		thumb_nail = request.FILES['thumbnail_img']
		cate = request.POST['category']
		user_obj = User.objects.get(username=request.user)
		upload_video = VideoPost(user=user_obj, title=title, desc=desc, video_file=video_file, thumbnail=thumb_nail, category=cate)
		upload_video.save()
		messages.success(request, 'Video has been uploaded.')

	return render(request, 'upload_video.html')


def watch_video(request, video_id):
	try:
		video_obj = VideoPost.objects.get(id=video_id)
	except ObjectDoesNotExist:
		return render(request, '404.html')
	try:
		session_obj = User.objects.get(username=request.user.username)
		val=1
	except:
		val=0
		# messages.warning(request, 'You are not login to watch this video.')
		# return redirect('home')

	video_comments = Comment.objects.filter(post=video_obj).order_by('-id')

	try:
		session1_obj = User.objects.get(username=video_obj.user)
	except ObjectDoesNotExist:
		return render(request, '404.html')
	profile_data = UserData.objects.get_or_create(user=session1_obj)[0]
	user_posts = VideoPost.objects.filter(user=session1_obj).order_by('-id')

	# Increase Views of Video if User visit this page
	if val:
		if request.user not in video_obj.video_views.all():
			video_obj.video_views.add(request.user)


		
		# Increase Likes of Video if User like this video
		
		is_liked = False
		if session_obj in video_obj.likes.all():
			is_liked = True
		else:
			is_liked = False
		params = {'video':video_obj, 'comments': video_comments, 'is_liked':is_liked,'session1':session1_obj,'user_data':profile_data,'val':val}
	if val:
		return render(request, 'watch_video.html', params)
	else:
		return render(request, 'watch_video.html',{'video':video_obj, 'comments': video_comments})	
	




def add_comment(request):
	if request.method == 'GET':
		video_id = request.GET['video_id']
		comment = request.GET['comment_text']
		video_obj = VideoPost.objects.get(id=video_id)
		session_obj = User.objects.get(username=request.user.username)
		video_comments = Comment.objects.filter(post=video_obj).order_by('-id')
		create_comment = Comment.objects.create(post=video_obj, user=session_obj, comment=comment)
		create_comment.save()

	return JsonResponse({'comment':create_comment.comment, 'count_comments':video_comments.count()})





def add_like(request, video_id):
	user_obj = User.objects.get(username=request.user.username)
	video_obj = VideoPost.objects.get(id=video_id)
	is_liked = False
	if user_obj in video_obj.likes.all():
		video_obj.likes.remove(user_obj)
		is_liked = True
	else:
		video_obj.likes.add(user_obj)
		is_liked = False
	return JsonResponse({'is_liked':is_liked,'likes_count':video_obj.likes.all().count()})




def profile(request, session_username):
	try:
		session_obj = User.objects.get(username=session_username)
	except ObjectDoesNotExist:
		return render(request, '404.html')
	profile_data = UserData.objects.get_or_create(user=session_obj)[0]
	user_posts = VideoPost.objects.filter(user=session_obj).order_by('-id')

	
	# Category wise Posts
	
	video_cat_science = VideoPost.objects.filter(user=session_obj, category='Science & Techanology').order_by('-id')
	video_cat_blogs = VideoPost.objects.filter(user=session_obj, category='Blogs').order_by('-id')
	video_cat_fashion = VideoPost.objects.filter(user=session_obj, category='Fashion').order_by('-id')
	video_cat_education = VideoPost.objects.filter(user=session_obj, category='Education').order_by('-id')
	video_cat_food = VideoPost.objects.filter(user=session_obj, category='Food').order_by('-id')
	
	subscribed = False
	if request.user in profile_data.subscribers.all():
		subscribed = True
	else:
		subscribed = False
	params = {'subscribed':subscribed,'session_obj':session_obj,'user_data':profile_data, 'videos': user_posts, 'sci': video_cat_science, 'blogs': video_cat_blogs, 'fashion': video_cat_fashion, 'edu':video_cat_education, 'food': video_cat_food}
	return render(request, 'profile.html', params)

def dashboard(request, session_username):
	user_videos = VideoPost.objects.filter(user__username=request.user.username).order_by('-id')
	user_data = UserData.objects.get_or_create(user=User.objects.get(username=request.user.username))[0]
	user_video_likes = 0
	user_videos_views = 0

	for video in user_videos:
		user_video_likes += video.likes.count()
		user_videos_views += video.video_views.count()


	params = {'videos': user_videos, 'user_data': user_data, 'total_likes':user_video_likes, 'total_views': user_videos_views}
	return render(request, 'dashboard.html', params)


def add_sub(request, viewer):
	viewer_obj = UserData.objects.get_or_create(user=User.objects.get(username=viewer))[0]
	subscriber_obj = User.objects.get(username=request.user.username)
	
	subscribed = False
	if subscriber_obj in viewer_obj.subscribers.all():
		viewer_obj.subscribers.remove(subscriber_obj)
		subscribed = True
	else:
		viewer_obj.subscribers.add(subscriber_obj)
		subscribed = False
	
	return JsonResponse({'is_subscribed': subscribed, 'viewer_obj':viewer_obj.subscribers.all().count()})



def edit_video(request, video_id):
	if request.method == 'POST':
		new_title = request.POST['new_title']
		new_desc = request.POST['new_desc']
		new_cate = request.POST['new_cate']

		video_obj = VideoPost.objects.get(id=video_id)
		video_obj.title = new_title
		video_obj.desc = new_desc
		video_obj.category = new_cate
		video_obj.save()
		
		return HttpResponseRedirect(reverse('dashboard', args=[str(request.user.username)]))
	else:
		return HttpResponse('get')




def update_details(request):
	if request.method == 'POST':
		user_data = UserData.objects.get(user=request.user)
		
		aboutText = request.POST['about_text']
		try:
			imgFile = request.FILES['img_field']
			if imgFile:
				user_data.profile_pic = imgFile
				
		except:
			print('some error occured')
		
		
		user_data.about = aboutText
		user_data.save()
	
		return HttpResponseRedirect(reverse('dashboard', args=[str(request.user.username)]))
	return redirect('dashboard')
	


def delete_video(request):
	if request.method == 'GET':
		vid = request.GET['videoId']
		video_obj = VideoPost.objects.get(id=vid)
		video_obj.delete()

		user_videos = VideoPost.objects.filter(user__username=request.user.username)
		user_video_likes = 0
		for video in user_videos:
			user_video_likes += video.likes.count()
		return JsonResponse({'video_id': vid, 'videosCount': user_videos.count(), 'videosLikes': user_video_likes})
	else:
		return JsonResponse({'status': 'not ok'})




def signup(request):
	if request.method == 'POST':
		first_name = request.POST['fname']
		mail = request.POST['mail']
		pwd = request.POST['pwd']
		if User.objects.filter(email=mail).exists():
			messages.warning(request,'Mail Already Exists')
			return redirect('home')
		if User.objects.filter(username=first_name).exists():
			messages.warning(request,'Channel Name Already Exists')
			return redirect('home')
		else:
			global ffnam,mmail,ppass
			ffnam=first_name
			mmail=mail
			ppass=pwd
			global n
			n=random.randint(10005000,99999999)
			str1="The OTP from Mr.K Videos is "
			str2=" . If you not tried to register in Mr.K Videos Leave it."
			str3=str1+str(n)+str2
			send_mail('OTP From Mr.K Videos ', str3, 'god3vishnu420@gmail.com', [mail],fail_silently=False)
			return redirect('otp')
			# new_user = User.objects.create_user(f'{first_name.lower()}', mail, pwd)
			# new_user.first_name = first_name
			# new_user.save()
			# messages.success(request, 'Account has been created successfully.')
	return redirect('home')

def otp(request):
	if request.method=='POST':
		otp=request.POST['otp']
		if int(otp)==int(n):
			new_user=User.objects.create_user(f'{ffnam.lower()}', mmail, ppass)
			new_user.first_name=ffnam
			new_user.save()
			messages.success(request, 'Account has been created successfully.')
			login(request, new_user)
			return redirect('home')
			
		else:
			return render(request, "otp.html")
	else:
		return render(request, "otp.html")			

def user_login(request):
	
	if not request.user.is_authenticated:

		if request.method == 'POST':
			uname = request.POST['uname']
			pwd = request.POST['pwd']
			
			usname=uname
			if uname=='admin':
				print(usname)
				return redirect('adm')
			else:	
				check_user = authenticate(username = uname, password = pwd)
				if check_user is not None:
					print(check_user)
					login(request, check_user)
					return redirect('home')
				else:
					messages.warning(request, 'Invalid Username or Password.')
					return redirect('home')
		return redirect('home')

	else:
		return redirect('home')



def user_logout(request):
	logout(request)
	return redirect('home')

def deleteac(request):
	if request.method=='POST':
		uname = request.POST['uname']
		if uname==request.user.username:
			udelete=User.objects.get(username=uname)
			print(udelete)
			udelete.delete()
			return redirect('home')
		else:
			return render(request,'dashboard.html')
	else:
		return redirect('dashboard')			

def report(request, video_id):
	return render(request,'report.html',{'video_id':video_id})	

def reportsub(request):
	if request.method=='POST':
		vid=request.POST['video_id']
		reson=request.POST['reason']
		try:
			video_obj = VideoPost.objects.get(id=vid)
			usiiname=User.objects.get(username=video_obj.user)
			sub='Your video '+video_obj.title+' is Delete From Mr.K Videos'
			mes1='Your video '+video_obj.title+' is Reported by '+request.user.username+'\nThe reason to report your video is\"'+reson+'\".'
			print(usiiname)
			print(usiiname.email)
			video_obj.delete()
			print(vid)
			print(reson)
			send_mail(sub, mes1, 'god3vishnu420@gmail.com', [usiiname.email],fail_silently=False)

			return redirect('home')
		except ObjectDoesNotExist:
			return render(request, '404.html')
	else:
		return redirect('home')				