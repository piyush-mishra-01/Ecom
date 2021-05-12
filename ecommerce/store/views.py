from ecommerce.settings import RAZORPAY_API_KEY, RAZORPAY_API_SECRET_KEY
from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.views.decorators.csrf import csrf_exempt
import razorpay
import datetime
import json
from .models import *
from .utils import *


# RazorPay client
client = razorpay.Client(
    auth=(RAZORPAY_API_KEY, RAZORPAY_API_SECRET_KEY))


# This will show details of product
def productDetail(request, slug):
    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.filter(slug=slug).first()
    context = {"products": products, 'cartItems': cartItems}
    return render(request, 'store/productdetail.html', context)


def store(request):
    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all()
    context = {"products": products, 'cartItems': cartItems}
    return render(request, 'store/store.html', context)


def product(request):
    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all()
    context = {"products": products, 'cartItems': cartItems}
    return render(request, 'store/product.html', context)


def search(request):
    try:
        q = request.GET['q']
        data = cartData(request)
        cartItems = data['cartItems']
        products = Product.objects.all().filter(name__icontains=q)
        context = {"products": products, 'cartItems': cartItems}
        return render(request, 'store/search.html', context)
    except:
        return HttpResponse("404 Page Not Found")


def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    if request.user.is_authenticated:
        if request.method == 'POST':
            customer = request.user.customer
            purchased = PurchasedOrder.objects.filter(customer=customer).last()
            shippingAddress = ShippingAddress.objects.filter(
                customer=customer, purchased_order=purchased).last()
            address = request.POST['address']
            mobile = request.POST['mobile']
            city = request.POST['city']
            state = request.POST['state']
            zipcode = request.POST['zipcode']

            if shippingAddress:
                shippingAddress.address = address
                shippingAddress.mobile = mobile
                shippingAddress.city = city
                shippingAddress.state = state
                shippingAddress.zipcode = zipcode
                shippingAddress.save()
            else:
                ShippingAddress.objects.create(
                    customer=customer,
                    purchased_order=purchased,
                    address=address,
                    mobile=mobile,
                    city=city,
                    state=state,
                    zipcode=zipcode
                )

            purchased.cart_quantity = order.get_cart_items
            purchased.price = order.get_cart_total
            purchased.save()

            return redirect('/payment')

        context = {'items': items, 'order': order, 'cartItems': cartItems}
        return render(request, 'store/checkout.html', context)

    else:
        return redirect('/login')


def payment(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    callback_url = 'http://' + str(get_current_site(request)) + '/handlerequest'

    if request.user.is_authenticated:
        customer = request.user.customer
        purchased = PurchasedOrder.objects.filter(customer=customer).last()
        orderId = purchased.order_id
        amount = float(order.get_cart_total)*100
        currency = 'INR'
        notes = {'Plateform': 'WatchShop',
                 'CallbackURL': callback_url, 'WatchSop Order Id': orderId}

        if amount > 1:
            payment = client.order.create(dict(
                amount=amount, currency=currency, receipt=orderId, notes=notes, payment_capture='1'))
            print(payment['id'])
            purchased.razorpay_order_id = payment['id']
            purchased.save()

            context = {'items': items, 'order': order, 'cartItems': cartItems,
                       'api_key': RAZORPAY_API_KEY, 'order_id': payment['id'], 'callback_url': callback_url}
            return render(request, 'store/payment.html', context)

        else:
            return HttpResponse("Minimum ammount must be INR 1 for checkout")

    else:
        return redirect("/login")


# Getting paymentID and SignatureID
@csrf_exempt
def handlerequest(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    if request.user.is_authenticated:
        if request.method == 'POST':
            try:
                payment_id = request.POST.get('razorpay_payment_id', '')
                order_id = request.POST.get('razorpay_order_id', '')
                signature = request.POST.get('razorpay_signature', '')
                params_dict = {
                    'razorpay_payment_id': payment_id,
                    'razorpay_order_id': order_id,
                    'razorpay_signature': signature
                }

                try:
                    purchased = PurchasedOrder.objects.get(
                        razorpay_order_id=order_id)
                except:
                    return HttpResponse("Razorpay orderId did not matched")

                purchased.razorpay_payment_id = payment_id
                purchased.razorpay_signature = signature
                purchased.save()

                result = client.utility.verify_payment_signature(params_dict)
                print(result)
                if result == None:
                    purchased.payment_status = 1
                    purchased.save()

                    orderItem = OrderItem.objects.get(order=order)
                    orderItem.delete()
                    context = {'items': items, 'order': order,
                               'cartItems': cartItems, 'shipping': False, }
                    return render(request, 'store/paymentsuccess.html', context)
                else:
                    purchased.payment_status = 2
                    purchased.save()
                    context = {'items': items, 'order': order,
                               'cartItems': cartItems, 'shipping': False, }
                    return render(request, 'store/paymentfailed.html', context)
            except:
                return HttpResponse("params_dict Not Captured")

        else:
            return HttpResponse("Its not a post request")
    else:
        return HttpResponse("404 Not Found")


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action :', action)
    print('productId :', productId)
    customer = request.user.customer
    product = Product.objects.get(id=productId)
    # below line attaches the order to the given customer
    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)
    # in the below line, we r using 'get_or_create' to change the values of orderItem, if it already exists
    # so, if it already exists, we don't wan't to create orderItem again, we just want to change the quantity of orderItem
    orderItem, created = OrderItem.objects.get_or_create(
        order=order, product=product)

    if action == 'add':
        # by clicking up arrow, increment orderItem by 1
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        # by clicking up arrow, decrement orderItem by 1
        orderItem.quantity = (orderItem.quantity - 1)

    # save quantity of products, for an order
    orderItem.save()

    if orderItem.quantity <= 0:
        # remove the orderItem from cart, when quantity reaches 0, or below it
        orderItem.delete()

    # get data for purchased items
    if PurchasedOrder.objects.exists():
        purchased = PurchasedOrder.objects.filter(customer=customer).last()
        purchased_Items, created = PurchasedItems.objects.get_or_create(
            product=product, purchased_order=purchased)
        purchased_Items.quantity = orderItem.quantity
        purchased_Items.save()
        if purchased_Items.quantity <= 0:
            # remove the orderItem from cart, when quantity reaches 0, or below it
            purchased_Items.delete()

    return JsonResponse('Item was added', safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)

    else:
        # guestOrder function is present in utils.py
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            mobile=data['shipping']['mobile'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse("Payment submitted...", safe=False)


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
                return redirect("/signup")

            # unique email ID
            if email and User.objects.filter(email=email).exists():
                messages.error(request, "Email already exist")
                return redirect("/signup")

            if username and User.objects.filter(username=username).exists():
                messages.error(request, "username already exist")
                return redirect("/signup")

            # length of password
            if len(pass1) < 6:
                messages.error(
                    request, "Password must be more than 6 characters")
                return redirect("/signup")

            # Passwords should match
            if pass1 != pass2:
                messages.error(request, "Passwords do not match")
                return redirect("/signup")

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
                             " Your account has been succesfully created")
            return redirect("/login")
    else:
        return redirect("/")

    context = {'items': items, 'order': order,
               'cartItems': cartItems, 'shipping': False, }
    return render(request, 'store/signup.html', context)


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
                return redirect("/login")
    else:
        return redirect("/")

    context = {'items': items, 'order': order,
               'cartItems': cartItems, 'shipping': False, }
    return render(request, 'store/login.html', context)


def handleLogout(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect("/")
    else:
        return redirect("/")


def contact(request):
    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all()
    context = {"products": products, 'cartItems': cartItems}
    return render(request, 'store/contact.html', context)
