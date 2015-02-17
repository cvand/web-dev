from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.db import transaction
from django.core.exceptions import ValidationError

from socialnetwork.models import *
from socialnetwork.forms import RegistrationForm, PostForm, EditUserForm, EditInfoForm
from django.core.context_processors import request
from django.http.response import HttpResponse
# from socialnetwork.forms import RegistrationForm, PostForm, EditForm

@login_required
def home(request):
    user = request.user
    userinfo = UserInfo.objects.filter(user=user)[0]
    following = userinfo.following.all()
    following_users = []
    for f in following:
        following_users.append(f.user)
    
    
    posts = Post.objects.all().order_by('-creation_date')
    return render(request, 'socialnetwork/home.html', {'posts' : posts, 'form' : PostForm(), 'following' : following_users})

@login_required
def profile(request, id):
    context = {}
    context['user'] = request.user
    user = User.objects.filter(id=id)
    context['editable'] = False;
     
    if not user:
        posts = Post.objects.all().order_by('-creation_date')
        context['posts'] = posts
        return redirect(reverse('home'))
     
    user = user[0]
    userInfo = UserInfo.objects.filter(user=user)[0]
     
    posts = Post.objects.filter(user=user).order_by('-creation_date')
    context['posts'] = posts
     
    if user.id is request.user.id:
        context['editable'] = True;
     
        editinfo_form = EditInfoForm(instance=userInfo)
        context['edit_form'] = editinfo_form
         
        user_form = EditUserForm(initial={
                                'first_name': user.first_name,
                                'last_name': user.last_name,
                                'password1': user.password,
                                'password2': user.password,
                                })
        context['user_form'] = user_form
     
    return render(request, 'socialnetwork/profile.html', context)

@login_required
@transaction.atomic
def add_post(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        return redirect(reverse('home'))

    post_form = PostForm(request.POST)
    context['form'] = post_form

    # Validates the form.
    if not post_form.is_valid():
        return redirect(reverse('home'))

    # At this point, the form data is valid.  Register and login the user.
    new_post = Post(user=request.user, post_content=post_form.cleaned_data['post_content'])
    new_post.save()

    return redirect(reverse('home'))
    
@login_required
@transaction.atomic
def edit_profile(request):
    context = {}
    errors = []
    er_count = 0
    
    if request.method == 'GET':
        return redirect(reverse('profile', kwargs={'id':request.user.id}))
    
    userinfo_form = EditInfoForm(request.POST)
    user_form = EditUserForm(request.POST)
 
    # Validates the form.
    if (not userinfo_form.is_valid()) or (not user_form.is_valid()):
        try:
            userinfo_form.is_valid()
        except ValidationError, err:
            errors[er_count] = '; '.join(err.messages)
            er_count = er_count + 1
            
        try:
            user_form.is_valid()
        except ValidationError, err:
            errors[er_count] = '; '.join(err.messages)
        
        context['errors'] = errors
        context['edit_form'] = userinfo_form
        context['user_form'] = user_form
        context['user'] = request.user
        context['editable'] = True
        posts = Post.objects.filter(user=request.user).order_by('-creation_date')
        context['posts'] = posts
        
        return render(request, 'socialnetwork/profile.html', context)
             
     
    user_obj = User.objects.filter(id=request.user.id)
     
    if user_obj:
        user = user_obj[0]
        if (user_form.cleaned_data['changed_password']):
            user.set_password(user_form.cleaned_data['password1'])
            
        user.first_name=user_form.cleaned_data['first_name']
        user.last_name=user_form.cleaned_data['last_name']
        user.save()
         
        userinfo = UserInfo.objects.filter(user=user)[0]
        userinfo.age = userinfo_form.cleaned_data['age']
        userinfo.short_bio = userinfo_form.cleaned_data['short_bio']
        userinfo.image = userinfo_form.cleaned_data['image']
        userinfo.save()

    return redirect(reverse('profile', kwargs={'id':request.user.id}))

@login_required
def stream(request):
    user = request.user
    posts = []
    following = UserInfo.objects.filter(user=user)[0].following.all()
    following_users = []
    for f in following:
        following_users.append(f.user)
    
    for follow_user in following:
        user_posts = Post.objects.filter(user=follow_user.user)
        posts.extend(user_posts)
    
    posts.sort(reverse=True)
    return render(request, 'socialnetwork/stream.html', {'posts' : posts, 'user' : user, 'following' : following_users})

@login_required
def follow(request, user_id):
    context = {}

    if 'follow' not in request.GET:
        return redirect(reverse('home'))
    
    action = request.GET['follow'];
    follower_id = request.user.id
    following_id = user_id

    user_follower = User.objects.filter(id=follower_id)
    user_following = User.objects.filter(id=following_id)
    
    if (not user_follower) or (not user_following):
        context['errors'] = 'Please select an existing user'
        context['posts'] = Post.objects.all().order_by('-creation_date')
        context['form'] = PostForm()
        
        userinfo = UserInfo.objects.filter(user=request.user)[0]
        following = userinfo.following.all()
        
        following_users = []
        for f in following:
            following_users.append(f.user)
        context['following'] = following_users
        return render(request, 'socialnetwork/home.html', context)   
        
    userinfo_follower = UserInfo.objects.filter(user=user_follower)[0]
    userinfo_following = UserInfo.objects.filter(user=user_following)[0]
    
    following_exists = UserInfo.objects.filter(following=userinfo_following)
    if (action == u'follow') and (not following_exists):
        userinfo_follower.following.add(userinfo_following)
        userinfo_follower.save()
    elif (action == u'unfollow') and (following_exists):
        userinfo_follower.following.remove(userinfo_following)
        userinfo_follower.save()
        
    return HttpResponse();

@login_required
@transaction.atomic
def delete_post(request, post_id, pageref):
    errors = []
    
    # Deletes post if the logged-in user has an post matching the id
    try:
        post_to_delete = Post.objects.get(id=post_id, user=request.user)
        post_to_delete.delete()
    except get_object_or_404:
        errors.append('This post either does not exist or is owned by another user.')
    
    posts = Post.objects.all().order_by('-creation_date')
    userinfo = UserInfo.objects.filter(user=request.user)[0]
    following = userinfo.following.all()
    following_users = []
    for f in following:
        following_users.append(f.user)
    url = 'socialnetwork/home.html'
    
    if (pageref == 'profile'):
        posts = Post.objects.filter(user=request.user).order_by('-creation_date')
        url = 'socialnetwork/profile.html'

    context = {'posts' : posts, 'errors' : errors, 'following' : following_users}
    return render(request, url, context)


@transaction.atomic
def register(request):
    context = {}
    errors = []
    er_count = 0

    if request.method == 'GET':
        context['form'] = RegistrationForm()
        context['userinfo_form'] = EditInfoForm()
        return render(request, 'socialnetwork/register.html', context)

    form = RegistrationForm(request.POST)
    
    new_user_info = UserInfo()
    userinfo_form = EditInfoForm(request.POST, request.FILES, instance=new_user_info)

    try:
        userinfo_form.is_valid()
    except ValidationError, err:
        errors[er_count] = '; '.join(err.messages)
        er_count = er_count + 1

    try:
        form.is_valid()
    except ValidationError, err:
        errors[er_count] = '; '.join(err.messages)
    
    if (not form.is_valid()) or (not userinfo_form.is_valid()):
        context['form'] = form
        context['errors'] = errors
        context['userinfo_form'] = userinfo_form
        return render(request, 'socialnetwork/register.html', context)

    # At this point, the form data is valid.  Register and login the user.
    new_user = User.objects.create_user(username=form.cleaned_data['username'], 
                                        password=form.cleaned_data['password1'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'])
    new_user.save()

    new_user_info.user=new_user
    if (userinfo_form.cleaned_data['age']):
        new_user_info.age = userinfo_form.cleaned_data['age']
    if userinfo_form.cleaned_data['short_bio']:
        new_user_info.short_bio=userinfo_form.cleaned_data['short_bio']
    if userinfo_form.cleaned_data['image']:
        new_user_info.content_type = userinfo_form.cleaned_data['image'].content_type
    
    new_user_info.save()

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password1'])
    login(request, new_user)
    return redirect(reverse('home'))

