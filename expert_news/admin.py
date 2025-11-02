from django.contrib import admin
from .models import ExpertNews, NewsInteraction

@admin.register(ExpertNews)
class ExpertNewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'expert', 'category', 'language', 'is_urgent', 'is_published', 'created_at']
    list_filter = ['category', 'language', 'is_urgent', 'is_published', 'created_at']
    search_fields = ['title', 'content', 'expert__username']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(NewsInteraction)
class NewsInteractionAdmin(admin.ModelAdmin):
    list_display = ['farmer', 'news', 'liked', 'saved', 'listened', 'created_at']
    list_filter = ['liked', 'saved', 'listened', 'created_at']
    search_fields = ['farmer__username', 'news__title']