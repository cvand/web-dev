from django.shortcuts import render, redirect
from django.core.exceptions import ObjectDoesNotExist

# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required

# Used to create and manually log in a user
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate

# Django transaction system so we can use @transaction.atomic
from django.db import transaction

from socialnetwork.models import *
from django.core.context_processors import request

@login_required
def home(request):
    posts = Post.objects.all().order_by('-creation_date')
    return render(request, 'socialnetwork/home.html', {'posts' : posts})

@login_required
def profile(request, id):
    user = User.objects.filter(id=id)
    posts = Post.objects.filter(user=user).order_by('-creation_date')
    
    return render(request, 'socialnetwork/profile.html', {'posts' : posts, 'user' : request.user})

@login_required
@transaction.atomic
def add_post(request):
    errors = []

    # Creates a new post if it is present as a parameter in the request
    if not 'postcontent' in request.POST or not request.POST['postcontent']:
        errors.append('You must enter some content to post.')
    else:
        new_post = Post(content=request.POST['postcontent'], user=request.user)
        new_post.save()
        
    posts = Post.objects.all().order_by('-creation_date')
    context = {'posts' : posts, 'errors' : errors}
    return render(request, 'socialnetwork/home.html', context)
    

@login_required
@transaction.atomic
def delete_post(request, post_id, pageref):
    errors = []
    
    # Deletes post if the logged-in user has an post matching the id
    try:
        post_to_delete = Post.objects.get(id=post_id, user=request.user)
        post_to_delete.delete()
    except ObjectDoesNotExist:
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
    errors = []
    context['errors'] = errors

    # Just display the registration form if this is a GET request
    if request.method == 'GET':
        return render(request, 'socialnetwork/register.html', context)

    # Checks the validity of the form data
    if not 'first' in request.POST or not request.POST['first']:
        errors.append('First Name is required.')
    else:
        # Save the first in the request context to re-fill the first
        # field in case the form has errrors
        context['first'] = request.POST['first']

    if not 'last' in request.POST or not request.POST['username']:
        errors.append('Last name is required.')
    else:
        # Save the last in the request context to re-fill the last
        # field in case the form has errrors
        context['last'] = request.POST['last']

    if not 'username' in request.POST or not request.POST['username']:
        errors.append('Username is required.')
    else:
        # Save the username in the request context to re-fill the username
        # field in case the form has errrors
        context['username'] = request.POST['username']

    if not 'password1' in request.POST or not request.POST['password1']:
        errors.append('Password is required.')
    if not 'password2' in request.POST or not request.POST['password2']:
        errors.append('Confirm password is required.')

    if 'password1' in request.POST and 'password2' in request.POST \
            and request.POST['password1'] and request.POST['password2'] \
            and request.POST['password1'] != request.POST['password2']:
        errors.append('Passwords did not match.')

    if len(User.objects.filter(username=request.POST['username'])) > 0:
        errors.append('Username is already taken.')

    if errors:
        return render(request, 'socialnetwork/register.html', context)

    # Creates the new user from the valid form data
    new_user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'], first_name=request.POST['first'], last_name=request.POST['last'])
    new_user.save()

    # Logs in the new user and redirects to his/her todo list
    new_user = authenticate(username=request.POST['username'], \
                            password=request.POST['password1'])
    login(request, new_user)
    return redirect('/socialnetwork/')

