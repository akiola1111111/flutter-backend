from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'disease-reports', views.DiseaseReportViewSet, basename='disease-reports')
router.register(r'expert-recommendations', views.ExpertRecommendationViewSet, basename='expert-recommendations')

urlpatterns = [
    path('', include(router.urls)),
]