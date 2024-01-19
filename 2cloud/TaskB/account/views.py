from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect

from .forms import SignUpForm, LoginForm


# Create your views here.


def register(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirect to your login page
    else:
        form = SignUpForm()
        return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('product_list')  # Redirect to your home page
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html', {'form': LoginForm})


def user_logout(request):
    logout(request)
    return redirect('login')  # Redirect to your home page or any other page after logout

