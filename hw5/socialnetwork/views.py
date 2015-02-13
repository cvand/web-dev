from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.db import transaction

from socialnetwork.models import *
from socialnetwork.forms import RegistrationForm, PostForm
# from socialnetwork.forms import RegistrationForm, PostForm, EditForm

@login_required
def home(request):
    posts = Post.objects.all().order_by('-creation_date')
    return render(request, 'socialnetwork/home.html', {'posts' : posts, 'form' : PostForm()})

@login_required
def profile(request, id):
    user = User.objects.filter(id=id)
    posts = Post.objects.filter(user=user).order_by('-creation_date')
    
    return render(request, 'socialnetwork/profile.html', {'posts' : posts, 'user' : request.user})

@login_required
@transaction.atomic
def add_post(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = PostForm()
        posts = Post.objects.all().order_by('-creation_date')
        context['posts'] = posts
        return render(request, 'socialnetwork/home.html', context)

    post_form = PostForm(request.POST)
    context['form'] = post_form

    # Validates the form.
    if not post_form.is_valid():
        posts = Post.objects.all().order_by('-creation_date')
        context['posts'] = posts
        return render(request, 'socialnetwork/home.html', context)

    # At this point, the form data is valid.  Register and login the user.
    new_post = Post(user=request.user, post_content=post_form.cleaned_data['post_content'])
    new_post.save()

    posts = Post.objects.all().order_by('-creation_date')
    context['posts'] = posts
    return redirect(reverse('home'))
    

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
    url = 'socialnetwork/home.html'
    
    if (pageref == 'profile'):
        posts = Post.objects.filter(user=request.user).order_by('-creation_date')
        url = 'socialnetwork/profile.html'

    context = {'posts' : posts, 'errors' : errors}
    return render(request, url, context)


@transaction.atomic
def register(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = RegistrationForm()
        return render(request, 'socialnetwork/register.html', context)

    # Creates a bound form from the request POST parameters and makes the 
    # form available in the request context dictionary.
    form = RegistrationForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'socialnetwork/register.html', context)

    # At this point, the form data is valid.  Register and login the user.
    new_user = User.objects.create_user(username=form.cleaned_data['username'], 
                                        password=form.cleaned_data['password1'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'])
    new_user.save()

    # Logs in the new user and redirects to his/her todo list
    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password1'])
    login(request, new_user)
    return redirect(reverse('home'))

