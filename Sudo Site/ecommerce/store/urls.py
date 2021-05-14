from django.urls import path
from . import views

urlpatterns = [
    path('',views.store, name="store"),
    path('product/',views.product, name="product"),
    path('search/',views.search, name="search"),
    path('cart/',views.cart, name="cart"),
    path('checkout/',views.checkout, name="checkout"),
    path('update_item/',views.updateItem, name="update_item"),
    path('process_order/',views.processOrder, name="process_order"),
    path('signup/',views.handleSignup, name="signup"),
    path('login/',views.handleLogin, name="login"),
    path('logout/',views.handleLogout, name="logout"),
    path('handlerequest',views.handlerequest, name="handlerequest"),
    path('payment/',views.payment, name="payment"),
    path('contact/',views.contact, name="contact"),
    path('product_detail/<slug:slug>/',views.productDetail, name="product_detail")
]

