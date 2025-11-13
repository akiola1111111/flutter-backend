from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Product, ProductImage
from .serializers import (
    ProductSerializer, 
    ProductCreateSerializer,
    ProductUpdateSerializer
)

@method_decorator(csrf_exempt, name='dispatch')
class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        user = self.request.user
        queryset = Product.objects.filter(is_available=True)
        
        # Filter by category if provided
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
            
        # Filter by search query if provided
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(category__icontains=search)
            )
            
        # Filter by location if provided
        location = self.request.query_params.get('location')
        if location:
            queryset = queryset.filter(location__icontains=location)
        
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ProductCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ProductUpdateSerializer
        return ProductSerializer
    
    def perform_create(self, serializer):
        serializer.save(farmer=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_products(self, request):
        """Get products created by the current farmer"""
        if request.user.user_type != 'farmer':
            return Response(
                {"error": "Only farmers can access their products"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        products = Product.objects.filter(farmer=request.user)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def toggle_availability(self, request, pk=None):
        """Toggle product availability"""
        product = self.get_object()
        
        # Check if user owns the product
        if product.farmer != request.user:
            return Response(
                {"error": "You can only update your own products"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        product.is_available = not product.is_available
        product.save()
        
        serializer = self.get_serializer(product)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get all available product categories"""
        categories = Product.CATEGORY_CHOICES
        return Response([{'value': cat[0], 'label': cat[1]} for cat in categories])