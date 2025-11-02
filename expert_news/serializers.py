from rest_framework import serializers
from .models import ExpertNews, NewsInteraction
from django.contrib.auth import get_user_model

User = get_user_model()

class ExpertNewsSerializer(serializers.ModelSerializer):
    expert_name = serializers.CharField(source='expert.username', read_only=True)
    expert_profile = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    audio_url = serializers.SerializerMethodField()
    interaction = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ExpertNews
        fields = [
            'id', 'expert', 'expert_name', 'expert_profile', 'title', 
            'content', 'category', 'language', 'image', 'image_url',
            'audio_message', 'audio_url', 'audio_duration', 'is_urgent',
            'is_published', 'target_regions', 'created_at', 'updated_at',
            'interaction', 'like_count'
        ]
        read_only_fields = ['expert', 'created_at', 'updated_at']
    
    def get_expert_profile(self, obj):
        return {
            'username': obj.expert.username,
            'user_type': obj.expert.user_type,
            'phone_number': getattr(obj.expert, 'phone_number', None)
        }
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None
    
    def get_audio_url(self, obj):
        request = self.context.get('request')
        if obj.audio_message and request:
            return request.build_absolute_uri(obj.audio_message.url)
        return None
    
    def get_interaction(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                interaction = NewsInteraction.objects.get(
                    farmer=request.user, 
                    news=obj
                )
                return {
                    'liked': interaction.liked,
                    'saved': interaction.saved,
                    'listened': interaction.listened
                }
            except NewsInteraction.DoesNotExist:
                return {'liked': False, 'saved': False, 'listened': False}
        return None
    
    def get_like_count(self, obj):
        return NewsInteraction.objects.filter(news=obj, liked=True).count()

class ExpertNewsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpertNews
        fields = [
            'title', 'content', 'category', 'language', 'image',
            'audio_message', 'is_urgent', 'target_regions'
        ]
    
    def validate(self, data):
        # Ensure at least one of content or audio_message is provided
        if not data.get('content') and not data.get('audio_message'):
            raise serializers.ValidationError(
                "Either text content or audio message must be provided"
            )
        return data

class NewsInteractionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsInteraction
        fields = ['id', 'farmer', 'news', 'liked', 'saved', 'listened', 'created_at']
        read_only_fields = ['farmer', 'created_at']