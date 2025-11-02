from django.urls import path
from . import views

urlpatterns = [
    path('news/', views.ExpertNewsListCreateView.as_view(), name='expert-news-list'),
    path('news/<int:pk>/', views.ExpertNewsDetailView.as_view(), name='expert-news-detail'),
    path('news/interact/', views.NewsInteractionView.as_view(), name='news-interact'),
    path('news/saved/', views.saved_news, name='saved-news'),
    path('expert/stats/', views.expert_stats, name='expert-stats'),
]