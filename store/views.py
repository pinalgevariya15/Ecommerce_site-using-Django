# store/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from decimal import Decimal

from .models import (
    Product, Category, Cart, CartItem, Order, OrderItem,
    Review, Wishlist, WishlistItem, UserProfile, Coupon
)
from .forms import ProductReviewForm, CheckoutForm, UserRegistrationForm


# ==================== HOME & BROWSE ====================

def home(request):
    """Homepage with featured products"""
    featured_products = Product.objects.filter(
        status='active',
        is_featured=True
    )[:8]
    
    new_products = Product.objects.filter(
        status='active'
    ).order_by('-created_at')[:6]
    
    categories = Category.objects.all()[:8]
    
    context = {
        'featured_products': featured_products,
        'new_products': new_products,
        'categories': categories,
        'page_title': 'Welcome to EcomHub',
    }
    return render(request, 'store/home.html', context)


def product_list(request):
    """Browse all products with filtering and search"""
    products = Product.objects.filter(status='active')
    categories = Category.objects.all()
    
    # Search
    search_query = request.GET.get('q', '')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(short_description__icontains=search_query)
        )
    
    # Category filter
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Price range filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Rating filter
    min_rating = request.GET.get('rating')
    if min_rating:
        products = products.annotate(
            avg_rating=Avg('reviews__rating')
        ).filter(avg_rating__gte=min_rating)
    
    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    valid_sorts = [
        'name', '-name', 'price', '-price',
        'created_at', '-created_at'
    ]
    if sort_by in valid_sorts:
        products = products.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_id,
        'page_title': 'Products',
    }
    return render(request, 'store/product_list.html', context)


def product_detail(request, slug):
    """Product detail page"""
    product = get_object_or_404(Product, slug=slug, status='active')
    
    # Get reviews
    reviews = product.reviews.filter(is_approved=True).order_by('-created_at')
    review_count = reviews.count()
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Related products (same category)
    related_products = Product.objects.filter(
        category=product.category,
        status='active'
    ).exclude(id=product.id)[:4]
    
    # Review form
    review_form = ProductReviewForm()
    user_review = None
    can_review = False
    
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()
        # Check if user has purchased this product
        can_review = Order.objects.filter(
            user=request.user,
            items__product=product,
            status='delivered'
        ).exists() and not user_review
    
    # Wishlist check
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = WishlistItem.objects.filter(
            wishlist__user=request.user,
            product=product
        ).exists()
    
    context = {
        'product': product,
        'reviews': reviews,
        'review_count': review_count,
        'average_rating': round(average_rating, 2),
        'related_products': related_products,
        'review_form': review_form,
        'user_review': user_review,
        'can_review': can_review,
        'in_wishlist': in_wishlist,
        'page_title': product.name,
    }
    return render(request, 'store/product_detail.html', context)


# ==================== CART MANAGEMENT ====================

@login_required(login_url='login')
def view_cart(request):
    """View shopping cart"""
    try:
        cart = request.user.cart
    except Cart.DoesNotExist:
        cart = Cart.objects.create(user=request.user)
    
    # 1. DO THE MATH HERE FOR THE CART
    subtotal = cart.get_cart_total if cart.items.exists() else Decimal('0.00')
    shipping = Decimal('50.00') if subtotal > 0 else Decimal('0.00')
    tax = subtotal * Decimal('0.10')
    grand_total = subtotal + shipping + tax
    
    context = {
        'cart': cart,
        'subtotal': subtotal,
        'shipping': shipping,
        'tax': tax,
        'grand_total': grand_total,
        'page_title': 'Shopping Cart',
    }
    return render(request, 'store/cart.html', context)


@login_required(login_url='login')
@require_POST
def add_to_cart(request):
    """Add product to cart via AJAX"""
    data = json.loads(request.body)
    product_id = data.get('product_id')
    quantity = int(data.get('quantity', 1))
    
    try:
        product = Product.objects.get(id=product_id, status='active')
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        return JsonResponse({
            'success': True,
            'message': f'{product.name} added to cart',
            'cart_count': cart.get_cart_quantity,
            'cart_total': str(cart.get_cart_total),
        })
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Product not found'})


@login_required(login_url='login')
def update_cart_item(request, item_id):
    """Update cart item quantity"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            cart_item.delete()
        else:
            cart_item.quantity = quantity
            cart_item.save()
        
        messages.success(request, 'Cart updated')
    
    return redirect('view_cart')


@login_required(login_url='login')
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from cart')
    return redirect('view_cart')


@login_required(login_url='login')
def clear_cart(request):
    """Clear entire cart"""
    try:
        cart = request.user.cart
        cart.items.all().delete()
        messages.success(request, 'Cart cleared')
    except Cart.DoesNotExist:
        pass
    
    return redirect('view_cart')


# ==================== CHECKOUT & ORDERS ====================

@login_required(login_url='login')
def checkout(request):
    """Checkout page"""
    try:
        cart = request.user.cart
        if not cart.items.exists():
            messages.warning(request, 'Your cart is empty')
            return redirect('view_cart')
    except Cart.DoesNotExist:
        messages.warning(request, 'Your cart is empty')
        return redirect('view_cart')
    
    # 2. DO THE MATH HERE FOR THE CHECKOUT DISPLAY
    subtotal = cart.get_cart_total
    tax = subtotal * Decimal('0.10')
    shipping_cost = Decimal('50.00')
    grand_total = subtotal + tax + shipping_cost

    if request.method == 'POST':
        shipping_address = request.POST.get('shipping_address')
        billing_address = request.POST.get('billing_address')
        notes = request.POST.get('notes', '')

        if not shipping_address:
            messages.error(request, 'Please provide a shipping address.')
            return redirect('checkout')

        if not billing_address:
            billing_address = shipping_address

        order = Order.objects.create(
            user=request.user,
            shipping_address=shipping_address,
            billing_address=billing_address,
            notes=notes,
            subtotal=subtotal,
            tax=tax,
            shipping_cost=shipping_cost,
            total_amount=grand_total
        )
        
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.get_price,
            )
        
        cart.items.all().delete()
        messages.success(request, f'Order created! Let\'s complete your payment.')
        return redirect('payment', order_id=order.id)
    
    context = {
        'cart': cart,
        'subtotal': subtotal,
        'shipping': shipping_cost,
        'tax': tax,
        'grand_total': grand_total,
        'page_title': 'Checkout',
    }
    return render(request, 'store/checkout.html', context)

@login_required(login_url='login')
def payment(request, order_id):
    """Payment page with COD support"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if request.method == 'POST':
        # Grab the payment method chosen by the user in the HTML
        payment_method = request.POST.get('payment_method', 'card')
        
        if payment_method == 'cod':
            order.payment_status = 'pending'
            order.status = 'processing'
            order.payment_method = 'Cash on Delivery'
            messages.success(request, 'Order confirmed! You will pay on delivery.')
        else:
            order.payment_status = 'completed'
            order.status = 'processing'
            order.payment_method = 'Credit Card'
            messages.success(request, 'Payment successful! Your order is being processed.')
            
        order.save()
        return redirect('order_confirmation', order_id=order.id)
    
    context = {
        'order': order,
        'page_title': 'Payment',
    }
    return render(request, 'store/payment.html', context)


@login_required(login_url='login')
def order_confirmation(request, order_id):
    """Order confirmation page"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order,
        'page_title': 'Order Confirmation',
    }
    return render(request, 'store/order_confirmation.html', context)


@login_required(login_url='login')
def order_history(request):
    """User's order history"""
    orders = request.user.orders.all().order_by('-created_at')
    
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'page_title': 'Order History',
    }
    return render(request, 'store/order_history.html', context)


@login_required(login_url='login')
def order_detail(request, order_id):
    """Order detail page"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    context = {
        'order': order,
        'page_title': f'Order {order.order_number}',
    }
    return render(request, 'store/order_detail.html', context)


# ==================== REVIEWS ====================

@login_required(login_url='login')
@require_POST
def add_review(request, product_id):
    """Add product review"""
    product = get_object_or_404(Product, id=product_id)
    
    # Check if user has purchased the product
    has_purchased = Order.objects.filter(
        user=request.user,
        items__product=product,
        status='delivered'
    ).exists()
    
    if not has_purchased:
        return JsonResponse({'success': False, 'message': 'You must purchase this product to review it'})
    
    # Check if already reviewed
    existing_review = Review.objects.filter(
        product=product,
        user=request.user
    ).exists()
    
    if existing_review:
        return JsonResponse({'success': False, 'message': 'You already reviewed this product'})
    
    form = ProductReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.product = product
        review.user = request.user
        review.save()
        
        return JsonResponse({'success': True, 'message': 'Review submitted and awaiting approval'})
    
    return JsonResponse({'success': False, 'message': 'Invalid form data'})


# ==================== WISHLIST ====================

@login_required(login_url='login')
def view_wishlist(request):
    """View wishlist"""
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    items = wishlist.items.all().order_by('-added_at')
    
    context = {
        'wishlist': wishlist,
        'items': items,
        'page_title': 'My Wishlist',
    }
    return render(request, 'store/wishlist.html', context)


@login_required(login_url='login')
@require_POST
def add_to_wishlist(request, product_id):
    """Add product to wishlist"""
    product = get_object_or_404(Product, id=product_id, status='active')
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    
    wishlist_item, created = WishlistItem.objects.get_or_create(
        wishlist=wishlist,
        product=product
    )
    
    if created:
        message = f'{product.name} added to wishlist'
    else:
        message = f'{product.name} already in wishlist'
    
    return JsonResponse({'success': True, 'message': message})


@login_required(login_url='login')
def remove_from_wishlist(request, item_id):
    """Remove from wishlist"""
    item = get_object_or_404(WishlistItem, id=item_id, wishlist__user=request.user)
    item.delete()
    messages.success(request, 'Removed from wishlist')
    return redirect('view_wishlist')


# ==================== USER PROFILE ====================

@login_required(login_url='login')
def profile(request):
    """User profile"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        profile.phone = request.POST.get('phone', '')
        profile.address = request.POST.get('address', '')
        profile.city = request.POST.get('city', '')
        profile.state = request.POST.get('state', '')
        profile.postal_code = request.POST.get('postal_code', '')
        profile.country = request.POST.get('country', '')
        profile.bio = request.POST.get('bio', '')
        
        if request.FILES.get('profile_picture'):
            profile.profile_picture = request.FILES['profile_picture']
        
        profile.save()
        messages.success(request, 'Profile updated successfully')
        return redirect('profile')
    
    context = {
        'profile': profile,
        'page_title': 'My Profile',
    }
    return render(request, 'store/profile.html', context)


# ==================== AUTHENTICATION ====================

from django.contrib.auth.models import User # Make sure this is imported at the top

def register(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        # 1. Manually grab the data exactly as named in the custom HTML
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # 2. Check for missing data or mismatched passwords
        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return redirect('register')
            
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken!')
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already registered!')
            return redirect('register')

        # 3. Create the user manually
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # 4. Create the related profile, cart, and wishlist
        UserProfile.objects.create(user=user)
        Cart.objects.create(user=user)
        Wishlist.objects.create(user=user)
        
        messages.success(request, 'Registration successful! Please login.')
        return redirect('login')
    
    context = {
        'page_title': 'Register',
    }
    return render(request, 'store/register.html', context)


def user_login(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect(request.GET.get('next', 'home'))
        else:
            messages.error(request, 'Invalid credentials')
    
    context = {
        'page_title': 'Login',
    }
    return render(request, 'store/login.html', context)


@login_required(login_url='login')
def user_logout(request):
    """User logout"""
    logout(request)
    messages.success(request, 'You have been logged out')
    return redirect('home')


# ==================== CATEGORY ====================

def category_products(request, slug):
    """Products in a category"""
    category = get_object_or_404(Category, slug=slug)
    products = category.products.filter(status='active')
    
    # Apply filters
    search_query = request.GET.get('q', '')
    if search_query:
        products = products.filter(name__icontains=search_query)
    
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by in ['name', '-name', 'price', '-price', 'created_at', '-created_at']:
        products = products.order_by(sort_by)
    
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
        'page_title': f'{category.name} Products',
    }
    return render(request, 'store/category_products.html', context)


# ==================== ADMIN DASHBOARD ====================

@login_required(login_url='login')
def admin_dashboard(request):
    """Admin dashboard"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied')
        return redirect('home')
    
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_revenue = sum(o.total_amount for o in Order.objects.filter(status='delivered'))
    pending_orders = Order.objects.filter(status='pending').count()
    
    recent_orders = Order.objects.all().order_by('-created_at')[:5]
    low_stock = Product.objects.filter(stock__lte=5, status='active')
    
    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'pending_orders': pending_orders,
        'recent_orders': recent_orders,
        'low_stock': low_stock,
        'page_title': 'Admin Dashboard',
    }
    return render(request, 'store/admin_dashboard.html', context)

@login_required(login_url='login')
def cancel_order(request, order_id):
    """Securely cancel an order if it hasn't shipped yet"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Security check: Only allow POST requests so people can't cancel by just typing a URL
    if request.method == 'POST':
        # Only allow cancellation if the order hasn't shipped
        if order.status in ['pending', 'processing']:
            order.status = 'cancelled'
            order.save()
            messages.success(request, f'Order {order.order_number} has been successfully cancelled.')
        else:
            messages.error(request, 'This order cannot be cancelled because it has already been shipped or delivered.')
            
    return redirect('order_detail', order_id=order.id)
