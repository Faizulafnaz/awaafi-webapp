# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('menu/', views.product_list, name='menu'),
    path('my-basket/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:variant_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item_ajax, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('save-address/', views.save_address, name='save_address'),
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('checkout-success/', views.checkout_success, name='checkout_success'),
    path('stripe-webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('contact-us/', views.contact_us, name='contact_us'),
]
