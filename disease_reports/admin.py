from django.contrib import admin
from .models import DiseaseReport, ExpertRecommendation

@admin.register(DiseaseReport)
class DiseaseReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'farmer', 'crop_type', 'status', 'priority', 'created_at']
    list_filter = ['status', 'priority', 'crop_type', 'created_at']
    search_fields = ['title', 'description', 'farmer__username']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ExpertRecommendation)
class ExpertRecommendationAdmin(admin.ModelAdmin):
    list_display = ['disease_report', 'expert', 'created_at']
    list_filter = ['created_at', 'expert']
    search_fields = ['disease_report__title', 'expert__username', 'diagnosis']
    readonly_fields = ['created_at']