from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.template.defaultfilters import slugify
# Create your models here.


class Customer(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200, null=True)
    slug = models.SlugField(max_length=200, unique=True, null=True)
    SKUID = models.CharField(max_length=200, null=True)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    brand = models.CharField(max_length=20, null=True, blank=True)
    specs = models.TextField(null=True, blank=True)
    detail = models.TextField(null=True, blank=True)
    image = models.ImageField(null=True, blank=True)
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url
    

class Order(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, blank=True, null=True)
    complete = models.BooleanField(default=False, null=True, blank=False)
    transaction_id = models.CharField(max_length=200, null=True, blank=True)
    date_ordered = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str(self.id)

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
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total

    def __str__(self):
        return f"{str(self.order.id)} {self.product.name}"

# Conform order will be stored


class PurchasedOrder(models.Model):
    payment_status_choices = (
        (1, 'SUCCESS'),
        (2, 'PENDING/FAILURE')
    )
    cod_choices = (
        (1, 'YES'),
        (2, 'NO')
    )
    # customer
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, blank=True, null=True)
    # Order ID
    order_id = models.CharField(
        unique=True, max_length=500, null=True, blank=True, default=None)
    cart_quantity = models.IntegerField(default=0, null=True, blank=True)
    total_price = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    COD = models.IntegerField(
        choices=cod_choices, default=2)
    payment_status = models.IntegerField(
        choices=payment_status_choices, default=2)
    # RazorPay Models
    razorpay_order_id = models.CharField(max_length=500, null=True, blank=True)
    razorpay_payment_id = models.CharField(
        max_length=500, null=True, blank=True)
    razorpay_signature = models.CharField(
        max_length=500, null=True, blank=True)
    
    GSTIN = models.CharField(max_length=200, null=True, blank=True)
    date_ordered = models.DateTimeField(default=timezone.now)

    # Genarating unique orderID
    def save(self, *args, **kwargs):
        if self.order_id is None and self.date_ordered and self.id:
            self.order_id = self.date_ordered.strftime(
                'PAY%y%m%d') + str(self.id)
        return super().save(*args, **kwargs)

    def __str__(self):
        return str(self.id)


class PurchasedItems(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, blank=True, null=True)
    purchased_order = models.ForeignKey(
        PurchasedOrder, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total

    def __str__(self):
        return f"{str(self.purchased_order.id)} {self.product.name}"


class ShippingAddress(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, blank=True, null=True)
    purchased_order = models.ForeignKey(
        PurchasedOrder, on_delete=models.CASCADE, blank=True, null=True)
    address = models.TextField(null=True)
    mobile = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    zipcode = models.CharField(max_length=200, null=True)

    def __str__(self):
        return f"{str(self.purchased_order.id)} {self.address}"

class Contact(models.Model):
    name = models.CharField(max_length=200, null=True)
    mobile = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)
    message = models.TextField(null=True)
    
    def __str__(self):
        return self.name
    
