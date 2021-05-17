from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from store.utils import *
from store.models import *

# Create your views here.
def handleSignup(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    if request.user.is_anonymous:
        if request.method == 'POST':
            username = request.POST['username']
            email = request.POST['email']
            fname = request.POST['fname']
            lname = request.POST['lname']
            pass1 = request.POST['pass1']
            pass2 = request.POST['pass2']

            # username name must be less than 10 char
            if len(username) > 10:
                messages.error(
                    request, "Username name must be less than 10 characters")
                return redirect("/user/signup")

            # unique email ID
            if email and User.objects.filter(email=email).exists():
                messages.error(request, "Email already exist")
                return redirect("/user/signup")

            if username and User.objects.filter(username=username).exists():
                messages.error(request, "username already exist")
                return redirect("/user/signup")

            # length of password
            if len(pass1) < 6:
                messages.error(
                    request, "Password must be more than 6 characters")
                return redirect("/user/signup")

            # Passwords should match
            if pass1 != pass2:
                messages.error(request, "Passwords did not match")
                return redirect("/user/signup")


            # Create User
            myuser = User.objects.create_user(username, email, pass1)
            myuser.first_name = fname
            myuser.last_name = lname
            myuser.save()

            # Create Customer
            Customer.objects.create(
                user=myuser,
                name=f"{fname} {lname}",
                email=email
            )

            messages.success(request, username +
                             " Your accounts has been succesfully created")
            return redirect("/user/login")
    else:
        return redirect("/")

    context = {'items': items, 'order': order,
               'cartItems': cartItems, 'shipping': False, }
    return render(request, 'user/signup.html', context)


def handleLogin(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    if request.user.is_anonymous:
        if request.method == 'POST':
            loginusername = request.POST['loginusername']
            loginpass = request.POST['loginpass']
            user = authenticate(username=loginusername, password=loginpass)

            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                messages.error(
                    request, "Invalid Credentials, Please try again")
                return redirect("/user/login")
    else:
        return redirect("/")

    context = {'items': items, 'order': order,
               'cartItems': cartItems, 'shipping': False, }
    return render(request, 'user/login.html', context)


def handleLogout(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect("/")
    else:
        return redirect("/")

@login_required
def profile(request):
    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all()
    context = {"products": products, 'cartItems': cartItems}
    return render(request, 'user/profile.html', context)
    
