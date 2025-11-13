from rest_framework import serializers
from .models import Product, ProductImage
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'user_type', 'phone_number', 'first_name', 'last_name']

class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'image_url', 'uploaded_at']
        read_only_fields = ['uploaded_at']
    
    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

class ProductSerializer(serializers.ModelSerializer):
    farmer_details = UserSerializer(source='farmer', read_only=True)
    image_url = serializers.SerializerMethodField()
    images = ProductImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'farmer', 'farmer_details', 'name', 'description', 
            'category', 'price', 'quantity', 'image', 'image_url', 'images',
            'contact_phone', 'location', 'is_available', 'created_at', 'updated_at'
        ]
        read_only_fields = ['farmer', 'created_at', 'updated_at']
    
    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

class ProductCreateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'category', 'price', 
            'quantity', 'contact_phone', 'location', 'images'
        ]
    
    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        validated_data['farmer'] = self.context['request'].user
        product = Product.objects.create(**validated_data)
        
        for image_data in images_data:
            ProductImage.objects.create(
                product=product,
                image=image_data
            )
        
        return product

class ProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'category', 'price', 
            'quantity', 'contact_phone', 'location', 'is_available'
        ]