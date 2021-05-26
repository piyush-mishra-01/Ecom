from django.urls import path
from . import views
urlpatterns = [
    path('',views.store, name="store"),
    path('product/',views.product, name="product"),
    path('search/',views.search, name="search"),
    path('cart/',views.cart, name="cart"),
    path('checkout/',views.checkout, name="checkout"),
    path('update_item/',views.updateItem, name="update_item"),
    path('handlerequest',views.handlerequest, name="handlerequest"),
    path('payment/',views.payment, name="payment"),
    path('contact/',views.contact, name="contact"),
    path('privacypolicy/',views.privacypolicy, name="privacypolicy"),
    path('conditions/',views.conditions, name="conditions"),
    path('refund/',views.refund, name="refund"),
    path('product_detail/<slug:slug>/',views.productDetail, name="product_detail")
]

