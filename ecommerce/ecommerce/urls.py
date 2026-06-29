"""
URL configuration for ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.contrib.auth import views as auth_views
from django.conf import settings
from store import views
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf import settings             # <--- THIS IS THE MAGIC LINE
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
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
    
    # ==================== ADMIN ====================
    path('', include('store.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)