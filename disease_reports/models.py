from django.db import models
from django.contrib.auth import get_user_model
import uuid
import os

User = get_user_model()

def disease_image_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('disease_images', filename)

def audio_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('disease_audio', filename)

class DiseaseReport(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_review', 'In Review'),
        ('resolved', 'Resolved'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    CROP_TYPE_CHOICES = [
        ('maize', 'Maize'),
        ('cassava', 'Cassava'),
        ('yam', 'Yam'),
        ('plantain', 'Plantain'),
        ('tomato', 'Tomato'),
        ('pepper', 'Pepper'),
        ('cocoa', 'Cocoa'),
        ('coffee', 'Coffee'),
        ('livestock', 'Livestock'),
        ('poultry', 'Poultry'),
        ('other', 'Other'),
    ]
    
    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='disease_reports')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    crop_type = models.CharField(max_length=100, choices=CROP_TYPE_CHOICES)
    location = models.CharField(max_length=100)
    image = models.ImageField(upload_to=disease_image_upload_path, null=True, blank=True)
    audio_note = models.FileField(upload_to=audio_upload_path, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    contact_phone = models.CharField(max_length=15, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Disease Report'
        verbose_name_plural = 'Disease Reports'
    
    def __str__(self):
        return f"{self.title} - {self.farmer.username}"

class DiseaseReportImage(models.Model):
    disease_report = models.ForeignKey(DiseaseReport, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=disease_image_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['uploaded_at']
        verbose_name = 'Disease Report Image'
        verbose_name_plural = 'Disease Report Images'
    
    def __str__(self):
        return f"Image for {self.disease_report.title}"

class ExpertRecommendation(models.Model):
    disease_report = models.ForeignKey(DiseaseReport, on_delete=models.CASCADE, related_name='recommendations')
    expert = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expert_recommendations')
    diagnosis = models.TextField()
    treatment_plan = models.TextField()
    preventive_measures = models.TextField(blank=True)
    audio_response = models.FileField(upload_to=audio_upload_path, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Expert Recommendation'
        verbose_name_plural = 'Expert Recommendations'
    
    def __str__(self):
        return f"Recommendation for {self.disease_report.title} by {self.expert.username}"