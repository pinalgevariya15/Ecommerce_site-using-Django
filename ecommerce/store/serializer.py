from rest_framework import serializers
from .models import Product, Cart, CartItem, Order, Review, UserProfile

class ProductSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    total_reviews = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'price', 'discount_price',
            'stock', 'category', 'featured_image', 'description',
            'average_rating', 'total_reviews', 'created_at'
        ]
    
    def get_average_rating(self, obj):
        return obj.average_rating
    
    def get_total_reviews(self, obj):
        return obj.total_reviews


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']
    
    def get_total_price(self, obj):
        return obj.get_total_price


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    item_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total', 'item_count']
    
    def get_total(self, obj):
        return obj.get_cart_total
    
    def get_item_count(self, obj):
        return obj.get_cart_quantity


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['product', 'product_name', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'status', 'payment_status',
            'total_amount', 'items', 'created_at', 'updated_at'
        ]
        read_only_fields = ['order_number', 'created_at', 'updated_at']


class ReviewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'product', 'user', 'username', 'rating',
            'title', 'comment', 'helpful_count', 'created_at'
        ]
        read_only_fields = ['user', 'helpful_count', 'created_at']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'phone', 'address', 'city', 'state',
            'postal_code', 'country', 'bio', 'profile_picture'
        ]