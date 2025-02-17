from django.shortcuts import render

from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password ==password2:
            if User.objects.filter(username=username, password=password):
                return({'error':'username already exists'})
                # messages.error(request"&&&&")
            else:
                user = User.objects.create_user(username=username, password=password)
                user.save()
                # messages.success(request,"yyyyyy")
        # else:
            # messages.error(request,"&y&y")
    return render(request, 'register.html')

def login_view(request):
    if request.method =='POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate (request, username=username, password=password)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            return render(request,'login.html',{'error':'invalid credentials'})
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def home(request):
    return render(request, 'home.html')