from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class ExpertNews(models.Model):
    CATEGORY_CHOICES = [
        ('farming_tips', 'Farming Tips'),
        ('disease_alerts', 'Disease Alerts'),
        ('market_news', 'Market News'),
        ('weather_alerts', 'Weather Alerts'),
        ('government_schemes', 'Government Schemes'),
        ('general', 'General News'),
    ]
    
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('tw', 'Twi'),
        ('ak', 'Akan'),
        ('ew', 'Ewe'),
        ('ga', 'Ga'),
        ('dag', 'Dagbani'),
    ]
    
    expert = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        limit_choices_to={'user_type': 'expert', 'is_approved': True}
    )
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True, null=True)  # Optional text content
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='general')
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='en')
    
    # Media fields
    image = models.ImageField(upload_to='expert_news/images/', blank=True, null=True)
    audio_message = models.FileField(upload_to='expert_news/audio/', blank=True, null=True)
    audio_duration = models.IntegerField(default=0, help_text="Audio duration in seconds")
    
    # Status fields
    is_urgent = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    target_regions = models.CharField(max_length=200, blank=True, help_text="Comma-separated regions")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Expert News'
    
    def __str__(self):
        return f"{self.title} by {self.expert.username}"
    
    @property
    def audio_url(self):
        if self.audio_message:
            return self.audio_message.url
        return None
    
    @property
    def image_url(self):
        if self.image:
            return self.image.url
        return None

class NewsInteraction(models.Model):
    """Track farmer interactions with news"""
    farmer = models.ForeignKey(User, on_delete=models.CASCADE)
    news = models.ForeignKey(ExpertNews, on_delete=models.CASCADE)
    liked = models.BooleanField(default=False)
    saved = models.BooleanField(default=False)
    listened = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['farmer', 'news']