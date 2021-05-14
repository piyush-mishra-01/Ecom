from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from store.utils import *

# Create your views here.
@login_required
def profile(request):
    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all()
    context = {"products": products, 'cartItems': cartItems}
    return render(request, 'user/profile.html', context)
    
