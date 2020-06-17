from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

# Create your views here.
def index(request):
    if not request.user.is_authenticated:
        return render(request, "login.html", {"message":None})
    context = {
        "user": request.user
    }
    return render(request, "user.html", context)

def login_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('index'))
    
    if request.method == 'GET':
        return render(request, 'login.html', {"message": None})

    username = request.POST['username']
    password = request.POST['password']

    # Server-side form validation
    if not username:
        return render(request, 'login.html', {"message": "No username."})
    elif len(username) < 4:
        return render(request, 'login.html', {"message": "Username should be longer than 4 characters."})
    elif not password:
        return render(request, 'login.html', {"message": "Type your password."})
    else:
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, 'login.html', {"message": "Login failed."})

def register_view(request):
    if request.method == 'GET':
        return render(request, 'register.html', {"message": None})

    username = request.POST['username']
    email = request.POST['email']
    password = request.POST['password']
    confirmation = request.POST['confirmation']

    # Server-side form validation
    if not username:
        return render(request, 'register.html', {"message": "No username."})
    elif len(username) < 4:
        return render(request, 'register.html', {"message": "Username should be longer than 4 characters."})
    elif not email:
        return render(request, 'register.html', {"message": "No Email."})
    # Email validation required.
    elif not password or not confirmation:
        return render(request, 'register.html', {"message": "Type your password."})
    elif len(password) < 8 or len(confirmation) < 8:
        return render(request, 'register.html', {"message": "Password should be longer than 8 characters."})
    elif password != confirmation:
        return render(request, 'register.html', {"message": "Passwords don't match."})
    elif User.objects.filter(email=email):
        return render(request, 'register.html', {"message": "Email is invalid or already taken."})
    else:
        try:
            User.objects.create_user(username, email, password)
        except:
            return render(request, 'register.html', {"message": "Registration failed."})

    return HttpResponseRedirect(reverse('login'))

def logout_view(request):
    logout(request)
    return render(request, "login.html", {"message": "You're Logged out"})