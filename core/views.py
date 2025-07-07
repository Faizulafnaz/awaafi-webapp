from django.shortcuts import render, redirect, get_object_or_404
from .models import Category, Product, Cart, CartItem, ProductVariant
from .utils import handle_exception
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import json
from decimal import Decimal
import stripe
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from .models import Order, OrderItem, Cart, CartItem
from accounts.models import Address
from django.core.mail import send_mail
from django.db import models



User = get_user_model()

stripe.api_key = settings.STRIPE_SECRET_KEY


def home(request):
    return render(request, 'home.html')


def product_list(request):
    categorized_products = {}
    search_query = request.GET.get('q', '').strip()
    search_results = None

    if search_query:
        # Search products by name or description (case-insensitive)
        search_results = Product.objects.filter(
            models.Q(name__icontains=search_query) | models.Q(description__icontains=search_query)
        ).prefetch_related('variants', 'category')
    else:
        try:
            categories = Category.objects.all()
            for category in categories:
                products = Product.objects.filter(category=category).prefetch_related('variants')
                categorized_products[category.name] = products
        except Exception as e:
            handle_exception(request, e, "Unable to load product list right now.")

    return render(request, 'menu.html', {
        'categorized_products': categorized_products,
        'search_results': search_results,
        'search_query': search_query,
    })



@login_required
def cart_detail(request):
    # Handle setting default address
    set_default_id = request.GET.get('set_default_address')
    if set_default_id:
        try:
            address = Address.objects.get(id=set_default_id, user=request.user)
            Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
            address.is_default = True
            address.save()
            messages.success(request, 'Default address updated!')
        except Address.DoesNotExist:
            messages.error(request, 'Address not found.')

    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('variant__product')
    cart_total = sum(item.variant.price * item.quantity for item in items)
    delivery_fee = Decimal('1.00')
    total_with_delivery = cart_total + delivery_fee

    # Fetch addresses
    addresses = Address.objects.filter(user=request.user)
    current_address = addresses.filter(is_default=True).first() or addresses.first()

    context = {
        'cart': cart,
        'items': items,
        'cart_total': cart_total,
        'delivery_fee': delivery_fee,
        'total_with_delivery': total_with_delivery,
        'addresses': addresses,
        'current_address': current_address,
        'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY,
    }
    return render(request, 'cart/cart_detail.html', context)


def add_to_cart(request, variant_id):
    # Check if user is authenticated
    if not request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': 'Please login to add items to cart',
                'redirect_url': '/accounts/login/'
            }, status=401)
        else:
            return redirect('/accounts/login/')
    
    variant = get_object_or_404(ProductVariant, id=variant_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, variant=variant)

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    # AJAX response
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Item added to cart',
            'cart_item_id': cart_item.id,
            'quantity': cart_item.quantity
        })

    # Fallback for normal request
    return redirect('cart_detail')


@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    return redirect('cart_detail')


@csrf_exempt
@login_required
def update_cart_item_ajax(request, item_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            item_id = item_id
            action = data.get('action')

            cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)

            if action == 'increase':
                cart_item.quantity += 1
            elif action == 'decrease':
                cart_item.quantity -= 1

            if cart_item.quantity < 1:
                cart_item.delete()
                return JsonResponse({'success': True, 'quantity': 0})

            cart_item.save()
            return JsonResponse({'success': True, 'quantity': cart_item.quantity})

        except CartItem.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Item not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


@login_required
def save_address(request):
    if request.method == 'POST':
        try:
            set_default = True if not Address.objects.filter(user=request.user).exists() else False
            if set_default:
                Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
            address = Address.objects.create(
                user=request.user,
                name=request.POST.get('name'),
                phone=request.POST.get('phone'),
                house=request.POST.get('house'),
                street=request.POST.get('street'),
                city=request.POST.get('city'),
                pin_code=request.POST.get('pin_code'),
                address_type=request.POST.get('address_type'),
                latitude=request.POST.get('latitude') or None,
                longitude=request.POST.get('longitude') or None,
                is_default=set_default,
            )
            messages.success(request, 'Address saved successfully!')
            return redirect('cart_detail')
        except Exception as e:
            messages.error(request, 'Failed to save address. Please try again.')
            return redirect('cart_detail')
    return redirect('cart_detail')




@login_required
@csrf_exempt
def create_checkout_session(request):
    if request.method == 'POST':
        # Check if user has a default address
        default_address = Address.objects.filter(user=request.user, is_default=True).first()
        if not default_address:
            return JsonResponse({
                'error': 'Please select a delivery address before proceeding to payment.'
            }, status=400)
        
        # Check if cart has items
        cart = Cart.objects.filter(user=request.user).first()
        if not cart or not cart.items.exists():
            return JsonResponse({
                'error': 'Your cart is empty. Please add items before proceeding to payment.'
            }, status=400)
        
        amount = int(float(request.POST.get('amount')) * 100)  # GBP in pence
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'gbp',
                    'product_data': {
                        'name': 'Awaafi Order',
                    },
                    'unit_amount': amount,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri('/checkout-success/'),
            cancel_url=request.build_absolute_uri('/my-basket/'),
            customer_email=request.user.email,
            metadata={
                'user_id': str(request.user.id),
            },
        )
        return JsonResponse({'id': session.id, 'url': session.url})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def checkout_success(request):
    # Optionally clear the cart here
    return render(request, 'cart/payment-success.html')



@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session['metadata']['user_id']
        user = User.objects.get(id=user_id)
        cart = Cart.objects.get(user=user)
        items = cart.items.select_related('variant__product')
        address = Address.objects.filter(user=user, is_default=True).first()
        total = sum(item.variant.price * item.quantity for item in items)

        # Create order
        order = Order.objects.create(
            user=user,
            address=address,
            total=total,
            status='paid',
            stripe_payment_intent=session.get('payment_intent', '')
        )
        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.variant.product,
                variant=item.variant,
                quantity=item.quantity,
                price=item.variant.price
            )
        # Clear cart
        items.delete()

    return HttpResponse(status=200)

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at').prefetch_related('items')
    return render(request, 'orders.html', {'orders': orders})

def contact_us(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        phone = request.POST.get('phone', '')
        email = request.POST.get('email', '')
        message = request.POST.get('message', '')
        captcha = request.POST.get('captcha', '')
        captcha_input = request.POST.get('captcha_input', '')

        # Simple captcha check (should be improved for production)
        if captcha.lower() != captcha_input.lower():
            messages.error(request, "Captcha is incorrect. Please try again.")
            return redirect('contact_us')

        send_mail(
            f"Contact Us: {name}",
            f"Name: {name}\nPhone: {phone}\nEmail: {email}\nMessage: {message}",
            settings.DEFAULT_FROM_EMAIL,
            [settings.CONTACT_EMAIL],  # Set this in your settings.py
            fail_silently=False,
        )
        messages.success(request, "Your enquiry has been sent successfully!")
        return redirect('contact_us')

    return render(request, 'contact_us.html')