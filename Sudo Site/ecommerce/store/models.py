from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200, null=True)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    slug = models.SlugField(max_length=200, unique=True, null=True) 
    available = models.BooleanField(default=True, null=True, blank=False)
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def imageURL(self): 
        try:
            url = self.image.url    
        except:
            url = ''
        return url 

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    date_ordered = models.DateTimeField(default=timezone.now )
    complete = models.BooleanField(default=False, null=True, blank=False)
    transaction_id = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return str(self.id)

    @property
    def shipping(self):
        shipping = False
        orderitems = self.orderitem_set.all()
        for i in orderitems:
            if i.product.available == True:
                shipping = True
        return shipping

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_ordered = models.DateTimeField(default=timezone.now )

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total
    
# Conform order will be stored
class PurchasedOrder(models.Model):
    payment_status_choices = (
        (1, 'SUCCESS'),
        (2, 'PENDING/FAILURE')
    )
    # customer
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    # Order ID
    order_id = models.CharField(unique=True, max_length=500, null=True, blank=True, default=None)
    date_ordered = models.DateTimeField(default=timezone.now, null=True, blank=True)
    cart_quantity = models.IntegerField(default=0, null=True, blank=True)
    price = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    payment_status = models.IntegerField(choices=payment_status_choices, default=2)
    # RazorPay Models
    razorpay_order_id = models.CharField(max_length=500, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=500, null=True, blank=True)
    razorpay_signature = models.CharField(max_length=500, null=True, blank=True)

    # Genarating unique orderID
    def save(self, *args, **kwargs):
        if self.order_id is None and self.date_ordered and self.id:
            self.order_id = self.date_ordered.strftime('PAY%y%m%d') + str(self.id)
        return super().save(*args, **kwargs)


    def __str__(self):
        return str(self.id)
    
class PurchasedItems(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    purchased_order = models.ForeignKey(PurchasedOrder, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total
    
class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    purchased_order = models.ForeignKey(PurchasedOrder, on_delete=models.SET_NULL, blank=True, null=True)
    address = models.TextField(null=True)
    mobile = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    zipcode = models.CharField(max_length=200, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address