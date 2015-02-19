import re

from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http.response import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404

from socialnetwork.forms import RegistrationForm, PostForm, EditUserForm, EditInfoForm
from socialnetwork.models import *


# from socialnetwork.forms import RegistrationForm, PostForm, EditForm
@login_required
def home(request):
    user = request.user
    following = Followers.objects.filter(follower = user)

    following_users = []
    for f in following:
        following_users.append(f.following)

    posts = Post.objects.all().order_by('-creation_date')
    return render(request, 'socialnetwork/home.html', {'posts' : posts, 'form' : PostForm(), 'following' : following_users, 'user' : user})

@login_required
def profile(request, id):
    context = {}
    logged_in_user = request.user
    context['user'] = logged_in_user
    user = User.objects.get(id = id)
    context['editable'] = False;

    if not user:
        posts = Post.objects.all().order_by('-creation_date')
        context['posts'] = posts
        return redirect(reverse('home'))

#     user = user[0]
#     userInfo = UserInfo.objects.filter(user=user)[0]
    userInfo = UserInfo.objects.get(user = user)

    context['profile_user'] = user
    following = Followers.objects.filter(follower = logged_in_user, following = userInfo)
    if following:
        context["following"] = True

    posts = Post.objects.filter(user = user).order_by('-creation_date')
    context['posts'] = posts

    if user.id is request.user.id:
        context['editable'] = True;

        editinfo_form = EditInfoForm(instance = userInfo)
        context['edit_form'] = editinfo_form

        user_form = EditUserForm(initial = {
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
    new_post = Post(user = request.user, post_content = post_form.cleaned_data['post_content'])
    new_post.save()

    return redirect(reverse('home'))

@login_required
@transaction.atomic
def edit_profile(request):
    context = {}
    errors = []
    er_count = 0

    if request.method == 'GET':
        return redirect(reverse('profile', kwargs = {'id':request.user.id}))

    user_info = UserInfo()
    userinfo_form = EditInfoForm(request.POST, request.FILES, instance = user_info)
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
        posts = Post.objects.filter(user = request.user).order_by('-creation_date')
        context['posts'] = posts

        return render(request, 'socialnetwork/profile.html', context)


    user = User.objects.get(id = request.user.id)

    if user:
        if (user_form.cleaned_data['changed_password']):
            user.set_password(user_form.cleaned_data['password1'])

        user.first_name = user_form.cleaned_data['first_name']
        user.last_name = user_form.cleaned_data['last_name']
        user.save()

        old_user_info = UserInfo.objects.get(user = user)
        if old_user_info and old_user_info.image:
            old_user_info.delete()

        user_info.user = user
        if userinfo_form.cleaned_data['image']:
            user_info.content_type = userinfo_form.cleaned_data['image'].content_type
        user_info.save()


    return redirect(reverse('profile', kwargs = {'id':request.user.id}))

@login_required
def stream(request):
    posts = []

    user = request.user
    following = Followers.objects.filter(follower = user)

    following_users = []
    for f in following:
        following_users.append(f.following)

    for follow_user in following_users:
        f_user = follow_user.user
        user_posts = Post.objects.filter(user = f_user)
        posts.extend(user_posts)

    posts.sort(key = lambda post: post.creation_date, reverse = True)
    return render(request, 'socialnetwork/stream.html', {'posts' : posts, 'user' : user, 'following' : following_users})

@login_required
def follow(request, user_id):
    context = {}

    if 'follow' not in request.GET:
        return redirect(reverse('home'))

    action = request.GET['follow'];
    follower_id = request.user.id
    following_id = user_id

    user_follower = User.objects.get(id = follower_id)
    user_following = User.objects.get(id = following_id)

    if (not user_follower) or (not user_following):
        context['errors'] = 'Please select an existing user'
        context['posts'] = Post.objects.all().order_by('-creation_date')
        context['form'] = PostForm()

        following = Followers.objects.filter(follower = request.user)

        following_users = []
        for f in following:
            following_users.append(f.following)
        context['following'] = following_users
        return render(request, 'socialnetwork/home.html', context)

    userinfo_following = UserInfo.objects.get(user = user_following)

    following_exists = Followers.objects.get(follower = user_follower, following = userinfo_following)
    if (action == u'follow') and (not following_exists):
        new_following = Followers(follower = user_follower, following = userinfo_following)
        new_following.save()
    elif (action == u'unfollow') and (following_exists):
        following_exists.delete()

    return HttpResponse();

@login_required
@transaction.atomic
def delete_post(request):
    errors = []
    kwargs = {}

    referer = get_referer_view(request, None)
    if 'stream' in referer:
        url = 'follower-stream'
        kwargs = {'id':request.user.id}
    elif 'profile' in referer:
        url = 'profile'
        kwargs = {'id':request.user.id}
    else:
        url = 'home'

    if request.method == 'GET':
        return redirect(reverse(url, kwargs = kwargs))

    post_id = request.POST['post_id']

    if not post_id:
        return redirect(reverse(url, kwargs = kwargs))

    try:
        post_to_delete = Post.objects.get(id = post_id, user = request.user)
        post_to_delete.delete()
    except get_object_or_404:
        errors.append('This post either does not exist or is owned by another user.')

    return redirect(reverse(url, kwargs = kwargs))


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
    userinfo_form = EditInfoForm(request.POST, request.FILES, instance = new_user_info)

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
    new_user = User.objects.create_user(username = form.cleaned_data['username'],
                                        password = form.cleaned_data['password1'],
                                        first_name = form.cleaned_data['first_name'],
                                        last_name = form.cleaned_data['last_name'])
    new_user.save()

    new_user_info.user = new_user
    if userinfo_form.cleaned_data['image']:
        new_user_info.content_type = userinfo_form.cleaned_data['image'].content_type

    new_user_info.save()

    new_user = authenticate(username = form.cleaned_data['username'],
                            password = form.cleaned_data['password1'])
    login(request, new_user)
    return redirect(reverse('home'))

def get_photo(request, id):
    user = User.objects.filter(id = id)
    userinfo = get_object_or_404(UserInfo, user = user)
    if not userinfo.image:
        raise Http404
    return HttpResponse(userinfo.image, content_type = userinfo.content_type)

def get_referer_view(request, default = None):
    # if the user typed the url directly in the browser's address bar
    referer = request.META.get('HTTP_REFERER')
    if not referer:
        return default

    # remove the protocol and split the url at the slashes
    referer = re.sub('^https?:\/\/', '', referer).split('/')

    # add the slash at the relative path's view and finished
    referer = u'/' + u'/'.join(referer[1:])
    return referer
