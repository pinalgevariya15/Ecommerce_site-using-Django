# store/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
# pyright: ignore [reportMissingImports]
from . import views

urlpatterns = [
    # ==================== HOME & BROWSE ====================
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('category/<slug:slug>/', views.category_products, name='category_products'),
    
    # ==================== AUTHENTICATION ====================
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='store/password_reset.html'
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='store/password_reset_done.html'
    ), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='store/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='store/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # ==================== CART ====================
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    
    # ==================== CHECKOUT & ORDERS ====================
    path('checkout/', views.checkout, name='checkout'),
    path('payment/<uuid:order_id>/', views.payment, name='payment'),
    path('order/<uuid:order_id>/confirmation/', views.order_confirmation, name='order_confirmation'),
    path('orders/', views.order_history, name='order_history'),
    path('order/<uuid:order_id>/', views.order_detail, name='order_detail'),
    
    # ==================== REVIEWS ====================
    path('product/<uuid:product_id>/review/add/', views.add_review, name='add_review'),
    
    # ==================== WISHLIST ====================
    path('wishlist/', views.view_wishlist, name='view_wishlist'),
    path('wishlist/add/<uuid:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:item_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    
    # ==================== USER PROFILE ====================
    path('profile/', views.profile, name='profile'),
    path('cancel-order/<uuid:order_id>/', views.cancel_order, name='cancel_order'),
    # ==================== ADMIN ====================
]
