from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'password2', 
                 'user_type', 'phone_number', 'address', 'first_name', 'last_name')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        # For experts, is_approved starts as False
        if attrs.get('user_type') == 'expert':
            attrs['is_approved'] = False
            
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            
            # Check if expert is approved
            if user.user_type == 'expert' and not user.is_approved:
                raise serializers.ValidationError('Expert account pending approval')
                
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include "username" and "password"')

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'user_type', 'phone_number', 
                 'address', 'first_name', 'last_name', 'profile_picture', 'is_approved')
        read_only_fields = ('id', 'user_type', 'is_approved')