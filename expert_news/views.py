from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Q
from .models import ExpertNews, NewsInteraction
from .serializers import (
    ExpertNewsSerializer, 
    ExpertNewsCreateSerializer,
    NewsInteractionSerializer
)

class ExpertNewsListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ExpertNewsCreateSerializer
        return ExpertNewsSerializer
    
    def get_queryset(self):
        queryset = ExpertNews.objects.filter(is_published=True)
        
        # Filter by category if provided
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Filter by language if provided
        language = self.request.query_params.get('language')
        if language:
            queryset = queryset.filter(language=language)
        
        # Filter by urgency if provided
        is_urgent = self.request.query_params.get('is_urgent')
        if is_urgent:
            queryset = queryset.filter(is_urgent=True)
        
        # Experts can see their own posts (including unpublished)
        if (self.request.user.user_type == 'expert' and 
            getattr(self.request.user, 'is_approved', False)):
            my_posts = self.request.query_params.get('my_posts')
            if my_posts == 'true':
                queryset = ExpertNews.objects.filter(expert=self.request.user)
        
        return queryset.order_by('-is_urgent', '-created_at')
    
    def perform_create(self, serializer):
        # Only approved experts can create news
        if (self.request.user.user_type != 'expert' or 
            not getattr(self.request.user, 'is_approved', False)):
            raise permissions.PermissionDenied(
                "Only approved experts can create news"
            )
        serializer.save(expert=self.request.user)

class ExpertNewsDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = ExpertNews.objects.all()
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ExpertNewsCreateSerializer
        return ExpertNewsSerializer
    
    def perform_update(self, serializer):
        # Only the expert who created the news can update it
        if serializer.instance.expert != self.request.user:
            raise permissions.PermissionDenied(
                "You can only update your own news posts"
            )
        serializer.save()

class NewsInteractionView(generics.CreateAPIView, generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NewsInteractionSerializer
    
    def get_queryset(self):
        return NewsInteraction.objects.filter(farmer=self.request.user)
    
    def create(self, request, *args, **kwargs):
        news_id = request.data.get('news')
        try:
            news = ExpertNews.objects.get(id=news_id)
        except ExpertNews.DoesNotExist:
            return Response(
                {"error": "News not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create or update interaction
        interaction, created = NewsInteraction.objects.get_or_create(
            farmer=request.user,
            news=news,
            defaults={
                'liked': request.data.get('liked', False),
                'saved': request.data.get('saved', False),
                'listened': request.data.get('listened', False)
            }
        )
        
        if not created:
            # Update existing interaction
            if 'liked' in request.data:
                interaction.liked = request.data['liked']
            if 'saved' in request.data:
                interaction.saved = request.data['saved']
            if 'listened' in request.data:
                interaction.listened = request.data['listened']
            interaction.save()
        
        serializer = self.get_serializer(interaction)
        return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def saved_news(request):
    """Get saved news by the current user"""
    saved_interactions = NewsInteraction.objects.filter(
        farmer=request.user, 
        saved=True
    ).select_related('news')
    
    saved_news_list = [interaction.news for interaction in saved_interactions]
    serializer = ExpertNewsSerializer(
        saved_news_list, 
        many=True, 
        context={'request': request}
    )
    
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def expert_stats(request):
    """Get statistics for experts"""
    if (request.user.user_type != 'expert' or 
        not getattr(request.user, 'is_approved', False)):
        return Response(
            {"error": "Only approved experts can access stats"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    total_posts = ExpertNews.objects.filter(expert=request.user).count()
    published_posts = ExpertNews.objects.filter(
        expert=request.user, 
        is_published=True
    ).count()
    
    # Calculate total likes
    expert_news = ExpertNews.objects.filter(expert=request.user)
    total_likes = NewsInteraction.objects.filter(
        news__in=expert_news, 
        liked=True
    ).count()
    
    return Response({
        'total_posts': total_posts,
        'published_posts': published_posts,
        'total_likes': total_likes
    })