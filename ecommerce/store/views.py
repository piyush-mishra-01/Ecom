from ecommerce.settings import DEFAULT_FROM_EMAIL, EMAIL_HOST_USER, RAZORPAY_API_KEY, RAZORPAY_API_SECRET_KEY
from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from django.contrib.sites.shortcuts import get_current_site
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
import razorpay
import json
from .models import *
from .utils import *
import math
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib import messages

# RazorPay client
client = razorpay.Client(
    auth=(RAZORPAY_API_KEY, RAZORPAY_API_SECRET_KEY))


def store(request):
    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all().order_by('-date_added')
    paginator = Paginator(products, 30)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    context = {"products": products, 'cartItems': cartItems}
    return render(request, 'store/store.html', context)


# This will show details of product
def productDetail(request, slug):
    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.filter(slug=slug).first()
    context = {"products": products, 'cartItems': cartItems}
    return render(request, 'store/productdetail.html', context)


def product(request):
    data = cartData(request)
    cartItems = data['cartItems']

    no_of_product = 30
    page = request.GET.get('page')
    if page is None:
        page = 1
    else:
        page = int(page)

    products = Product.objects.all().order_by('-date_added')
    length = len(products)
    products = products[(page-1)*no_of_product: page*no_of_product]
    if page > 1:
        prev = "?page=" + str(page - 1)
    else:
        prev = None
    if page < math.ceil(length/no_of_product):
        nxt = "?page=" + str(page + 1)
    else:
        nxt = None
    context = {"products": products,
        'cartItems': cartItems, 'prev': prev, 'nxt': nxt}
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


@login_required
def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

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
        gstin = request.POST['gstin']

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

        purchased.GSTIN = gstin
        purchased.cart_quantity = order.get_cart_items
        purchased.total_price = order.get_cart_total
        purchased.save()

        if request.POST.get('click', False):
            purchased.COD = 1
            purchased.save()

            # Emai conformation for COD to client + owner
            order_client_template = render_to_string('emails/order_client_template.html', {'name': request.user.customer.name,
                                        'items': items, 'order': order, 'cartItems': cartItems, 'orderID': purchased.order_id})
            text_content = strip_tags(order_client_template)
            email = EmailMultiAlternatives(
                'Thanks for purchasing from MASTRENA',
                text_content,
                DEFAULT_FROM_EMAIL,
                [request.user.email],
            )
            email.attach_alternative(order_client_template, "text/html")
            email.fail_silently = False
            email.send()

            order_template = render_to_string('emails/order_template.html', {'name': request.user.customer.name,
                                        'items': items, 'order': order, 'cartItems': cartItems, 'orderID': purchased.order_id,
                                        'email': request.user.customer.email})
            order_content = strip_tags(order_template)
            email = EmailMultiAlternatives(
                f"You have got a COD order for Order- ID {purchased.order_id}",
                order_content,
                DEFAULT_FROM_EMAIL,
                [EMAIL_HOST_USER],
            )
            email.attach_alternative(order_template, "text/html")
            email.fail_silently = False
            email.send()

            orderItem = OrderItem.objects.all()
            orderItem.delete()

            context = {'items': items, 'order': order,
                        'cartItems': cartItems, 'shipping': False, }
            return render(request, 'store/codsuccess.html', context)
        else:
            return redirect('/payment')

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)


@login_required
def payment(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    callback_url = 'http://' + \
        str(get_current_site(request)) + '/handlerequest'

    customer = request.user.customer
    purchased = PurchasedOrder.objects.filter(customer=customer).last()
    shippingAddress = ShippingAddress.objects.filter(
            customer=customer, purchased_order=purchased).last()
    orderId = purchased.order_id
    amount = float(order.get_cart_total)*100
    currency = 'INR'
    notes = {'Plateform': 'Mastrena',
                'CallbackURL': callback_url, 'Mastrena Order Id': orderId}

    if amount > 1:
        payment = client.order.create(dict(
            amount=amount, currency=currency, receipt=orderId, notes=notes, payment_capture='1'))
        purchased.razorpay_order_id = payment['id']
        purchased.save()

        context = {'items': items, 'order': order, 'cartItems': cartItems,
                    'api_key': RAZORPAY_API_KEY, 'order_id': payment['id'], 'callback_url': callback_url,
                    'name': request.user.customer.name, 'email': request.user.customer.email, 'mobile': shippingAddress.mobile}
        return render(request, 'store/payment.html', context)

    else:
        return HttpResponse("Minimum ammount must be INR 1 for checkout")


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
                if result == None:
                    purchased.payment_status = 1
                    purchased.save()

                    # Emai conformation for payment to client + owner
                    order_client_template = render_to_string('emails/order_client_template.html', {'name': request.user.customer.name,
                                        'items': items, 'order': order, 'cartItems': cartItems, 'orderID': purchased.order_id})
                    text_content = strip_tags(order_client_template)
                    email = EmailMultiAlternatives(
                        'Thanks for purchasing from MASTRENA',
                        text_content,
                        DEFAULT_FROM_EMAIL,
                        [request.user.email],
                    )
                    email.attach_alternative(order_client_template, "text/html")
                    email.fail_silently = False
                    email.send()

                    order_template = render_to_string('emails/order_template.html', {'name': request.user.customer.name,
                                                'items': items, 'order': order, 'cartItems': cartItems, 'orderID': purchased.order_id,
                                                'email': request.user.customer.email})
                    order_content = strip_tags(order_template)
                    email = EmailMultiAlternatives(
                        f"You have got a Prepaid order for Order- ID {purchased.order_id}",
                        order_content,
                        DEFAULT_FROM_EMAIL,
                        [EMAIL_HOST_USER],
                    )
                    email.attach_alternative(order_template, "text/html")
                    email.fail_silently = False
                    email.send()

                    orderItem = OrderItem.objects.all()
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


def contact(request):
    data = cartData(request)
    cartItems = data['cartItems']

    if request.method == 'POST':
        name = request.POST['name']
        mobile = request.POST['mobile']
        email = request.POST['email']
        message = request.POST['message']


    # contact email
        email = EmailMultiAlternatives(
                        f"A new message from {name}",
                        f"Name: {name} \nPhone No: {mobile} \nEmail: {email} \n\n\nMessage: \n {message}",
                        DEFAULT_FROM_EMAIL,
                        [EMAIL_HOST_USER],
                    )
        email.fail_silently = False
        email.send()
        messages.success(request, "Your message have been sent succesfully")

    products = Product.objects.all()
    context = {"products": products, 'cartItems': cartItems}
    return render(request, 'store/contact.html', context)