# store/admin.py
from django.contrib import admin
from django.utils.html import format_html
# pyright: ignore [reportMissingImports]
from .models import (
    Category, Product, ProductImage, Cart, CartItem,
    Order, OrderItem, Review, Wishlist, WishlistItem,
    UserProfile, Coupon
)

# ==================== PRODUCT ADMIN ====================

class ProductImageInline(admin.TabularInline):
    """Inline admin for product images"""
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'is_main', 'order')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin for product categories"""
    list_display = ('name', 'slug', 'get_product_count')
    list_filter = ('created_at',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_product_count(self, obj):
        return obj.products.count()
    get_product_count.short_description = 'Products'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin for products"""
    list_display = ('name', 'sku', 'get_price_display', 'stock', 'status', 'is_featured', 'average_rating')
    list_filter = ('status', 'category', 'is_featured', 'created_at')
    search_fields = ('name', 'sku', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at', 'average_rating', 'total_reviews')
    filter_horizontal = ()
    inlines = [ProductImageInline]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Product Information', {
            'fields': ('name', 'slug', 'category', 'sku', 'status')
        }),
        ('Pricing', {
            'fields': ('price', 'discount_price')
        }),
        ('Inventory', {
            'fields': ('stock',)
        }),
        ('Description', {
            'fields': ('short_description', 'description'),
            'classes': ('wide',)
        }),
        ('Images', {
            'fields': ('featured_image',)
        }),
        ('Features', {
            'fields': ('is_featured',)
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Reviews', {
            'fields': ('average_rating', 'total_reviews'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_price_display(self, obj):
        if obj.discount_price:
            return format_html(
                '<span style="text-decoration: line-through;">₹{}</span> <strong style="color: green;">₹{}</strong>',
                obj.price, obj.discount_price
            )
        return f"₹{obj.price}"
    get_price_display.short_description = 'Price'


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """Admin for product images"""
    list_display = ('product', 'is_main', 'order', 'created_at')
    list_filter = ('is_main', 'product__category')
    search_fields = ('product__name', 'alt_text')


# ==================== CART ADMIN ====================

class CartItemInline(admin.TabularInline):
    """Inline admin for cart items"""
    model = CartItem
    extra = 0
    readonly_fields = ('get_total_price',)
    fields = ('product', 'quantity', 'get_total_price')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin for shopping carts"""
    list_display = ('user', 'get_item_count', 'get_total_price', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at', 'get_total_price')
    inlines = [CartItemInline]
    
    def get_item_count(self, obj):
        return obj.items.count()
    get_item_count.short_description = 'Items'
    
    def get_total_price(self, obj):
        return format_html('₹{}', obj.get_cart_total)
    get_total_price.short_description = 'Total'


# ==================== ORDER ADMIN ====================

class OrderItemInline(admin.TabularInline):
    """Inline admin for order items"""
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price', 'get_total')
    fields = ('product', 'quantity', 'price', 'get_total')
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin for orders"""
    list_display = ('order_number', 'user', 'total_amount', 'status', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_status', 'created_at')
    search_fields = ('order_number', 'user__username', 'user__email')
    readonly_fields = ('order_number', 'created_at', 'updated_at', 'shipped_at', 'delivered_at')
    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user')
        }),
        ('Status', {
            'fields': ('status', 'payment_status')
        }),
        ('Addresses', {
            'fields': ('shipping_address', 'billing_address'),
            'classes': ('collapse',)
        }),
        ('Pricing', {
            'fields': ('subtotal', 'tax', 'shipping_cost', 'total_amount')
        }),
        ('Payment', {
            'fields': ('payment_method', 'transaction_id'),
            'classes': ('collapse',)
        }),
        ('Shipping', {
            'fields': ('tracking_number', 'shipped_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered']
    
    def mark_as_processing(self, request, queryset):
        queryset.update(status='processing')
    mark_as_processing.short_description = "Mark selected as Processing"
    
    def mark_as_shipped(self, request, queryset):
        queryset.update(status='shipped')
    mark_as_shipped.short_description = "Mark selected as Shipped"
    
    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')
    mark_as_delivered.short_description = "Mark selected as Delivered"


# ==================== REVIEW ADMIN ====================

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin for product reviews"""
    list_display = ('product', 'user', 'get_rating_display', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved', 'created_at')
    search_fields = ('product__name', 'user__username', 'title', 'comment')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Review Information', {
            'fields': ('product', 'user', 'rating', 'title')
        }),
        ('Content', {
            'fields': ('comment',),
            'classes': ('wide',)
        }),
        ('Moderation', {
            'fields': ('is_approved', 'helpful_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_reviews', 'reject_reviews']
    
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
    approve_reviews.short_description = "Approve selected reviews"
    
    def reject_reviews(self, request, queryset):
        queryset.update(is_approved=False)
    reject_reviews.short_description = "Reject selected reviews"
    
    def get_rating_display(self, obj):
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html('<span style="color: gold;">{}</span>', stars)
    get_rating_display.short_description = 'Rating'


# ==================== WISHLIST ADMIN ====================

class WishlistItemInline(admin.TabularInline):
    """Inline admin for wishlist items"""
    model = WishlistItem
    extra = 0
    readonly_fields = ('added_at',)


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    """Admin for wishlists"""
    list_display = ('user', 'get_item_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at',)
    inlines = [WishlistItemInline]
    
    def get_item_count(self, obj):
        return obj.items.count()
    get_item_count.short_description = 'Items'


# ==================== USER PROFILE ADMIN ====================

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin for user profiles"""
    list_display = ('user', 'phone', 'city', 'is_verified', 'newsletter_subscription', 'created_at')
    list_filter = ('is_verified', 'newsletter_subscription', 'created_at', 'country')
    search_fields = ('user__username', 'user__email', 'phone', 'city')
    readonly_fields = ('created_at', 'updated_at', 'get_email')
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Contact Information', {
            'fields': ('phone', 'get_email')
        }),
        ('Address', {
            'fields': ('address', 'city', 'state', 'postal_code', 'country')
        }),
        ('Profile', {
            'fields': ('profile_picture', 'bio')
        }),
        ('Preferences', {
            'fields': ('is_verified', 'newsletter_subscription')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_email(self, obj):
        return obj.user.email if obj.user else ""
    get_email.short_description = 'Email'


# ==================== COUPON ADMIN ====================

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    """Admin for coupons"""
    list_display = ('code', 'get_discount_display', 'usage_count', 'is_valid_display', 'valid_from', 'valid_until')
    list_filter = ('discount_type', 'is_active', 'valid_from', 'valid_until')
    search_fields = ('code', 'description')
    readonly_fields = ('created_at', 'usage_count')
    
    fieldsets = (
        ('Coupon Information', {
            'fields': ('code', 'description')
        }),
        ('Discount', {
            'fields': ('discount_type', 'discount_value', 'minimum_purchase')
        }),
        ('Usage', {
            'fields': ('usage_limit', 'usage_count', 'is_active')
        }),
        ('Validity', {
            'fields': ('valid_from', 'valid_until')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_discount_display(self, obj):
        symbol = '%' if obj.discount_type == 'percentage' else '₹'
        return f'{obj.discount_value}{symbol}'
    get_discount_display.short_description = 'Discount'
    
    def is_valid_display(self, obj):
        color = 'green' if obj.is_valid else 'red'
        status = 'Valid' if obj.is_valid else 'Invalid'
        return format_html('<span style="color: {};">{}</span>', color, status)
    is_valid_display.short_description = 'Status'


# ==================== ADMIN CUSTOMIZATION ====================

admin.site.site_header = "EcomHub Admin Panel"
admin.site.site_title = "EcomHub Administration"
admin.site.index_title = "Welcome to EcomHub Admin"
