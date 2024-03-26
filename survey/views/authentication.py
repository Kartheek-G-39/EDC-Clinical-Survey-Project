from django.shortcuts import render
from django.shortcuts import render, redirect,HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate , login as loginUser , logout
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
def login(request):
    if request.method == "POST":
            username=request.POST.get('username')
            password=request.POST.get('password')
            user = authenticate(request, username=username,password=password)
            if user is not None:
                login(request, user)

                return HttpResponse("login page")
            else:
            #    
                return HttpResponse("Failed")

def signup(request):
    if request.method == 'GET':

        form = UserCreationForm()
        context = {
            "form": form
        }
        return render(request, 'signup.html', context=context)
    else:
        print(request.POST)
        form = UserCreationForm(request.POST)
        context = {
            "form": form
        }
        if form.is_valid():
            user = form.save()
            print(user)
            if user is not None:
                return redirect('login')
        else:
            return render(request, 'signup.html', context=context)

def signout(request):
    logout(request)
    return redirect('home')