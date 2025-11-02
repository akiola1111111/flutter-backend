from rest_framework import serializers
from .models import DiseaseReport, DiseaseReportImage, ExpertRecommendation
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'user_type', 'phone_number']

class DiseaseReportImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = DiseaseReportImage
        fields = ['id', 'image', 'image_url', 'uploaded_at']
        read_only_fields = ['uploaded_at']
    
    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

class DiseaseReportSerializer(serializers.ModelSerializer):
    farmer_details = UserSerializer(source='farmer', read_only=True)
    image_url = serializers.SerializerMethodField()
    audio_url = serializers.SerializerMethodField()
    has_recommendations = serializers.SerializerMethodField()
    images = DiseaseReportImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = DiseaseReport
        fields = [
            'id', 'farmer', 'farmer_details', 'title', 'description', 
            'crop_type', 'location', 'contact_phone', 'image', 'image_url', 'audio_note', 
            'audio_url', 'status', 'priority', 'has_recommendations', 'images',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['farmer', 'created_at', 'updated_at']
    
    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None
    
    def get_audio_url(self, obj):
        if obj.audio_note:
            return obj.audio_note.url
        return None
    
    def get_has_recommendations(self, obj):
        return obj.recommendations.exists()

class DiseaseReportCreateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = DiseaseReport
        fields = [
            'title', 'description', 'crop_type', 'location', 
            'contact_phone', 'priority', 'images'
        ]
    
    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        validated_data['farmer'] = self.context['request'].user
        disease_report = DiseaseReport.objects.create(**validated_data)
        
        for image_data in images_data:
            DiseaseReportImage.objects.create(
                disease_report=disease_report,
                image=image_data
            )
        
        return disease_report

class ExpertRecommendationSerializer(serializers.ModelSerializer):
    expert_details = UserSerializer(source='expert', read_only=True)
    audio_url = serializers.SerializerMethodField()
    disease_report_title = serializers.CharField(source='disease_report.title', read_only=True)
    
    class Meta:
        model = ExpertRecommendation
        fields = [
            'id', 'disease_report', 'disease_report_title', 'expert', 'expert_details', 
            'diagnosis', 'treatment_plan', 'preventive_measures',
            'audio_response', 'audio_url', 'created_at'
        ]
        read_only_fields = ['expert', 'created_at']
    
    def get_audio_url(self, obj):
        if obj.audio_response:
            return obj.audio_response.url
        return None