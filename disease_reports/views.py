from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import DiseaseReport, ExpertRecommendation
from .serializers import (
    DiseaseReportSerializer, 
    ExpertRecommendationSerializer,
    DiseaseReportCreateSerializer
)

@method_decorator(csrf_exempt, name='dispatch')
class DiseaseReportViewSet(viewsets.ModelViewSet):
    serializer_class = DiseaseReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        user = self.request.user
        queryset = DiseaseReport.objects.all()
        
        if user.user_type == 'farmer':
            queryset = queryset.filter(farmer=user)
        elif user.user_type == 'expert':
            if not user.is_approved:
                return DiseaseReport.objects.none()
        else:
            return DiseaseReport.objects.none()
        
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        crop_type_filter = self.request.query_params.get('crop_type', None)
        if crop_type_filter:
            queryset = queryset.filter(crop_type=crop_type_filter)
            
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DiseaseReportCreateSerializer
        return DiseaseReportSerializer
    
    def perform_create(self, serializer):
        serializer.save(farmer=self.request.user)
    
    @action(detail=True, methods=['get'])
    def recommendations(self, request, pk=None):
        disease_report = self.get_object()
        recommendations = disease_report.recommendations.all()
        serializer = ExpertRecommendationSerializer(recommendations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_reports(self, request):
        if request.user.user_type != 'farmer':
            return Response(
                {"error": "This endpoint is only for farmers"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        reports = DiseaseReport.objects.filter(farmer=request.user)
        serializer = self.get_serializer(reports, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        disease_report = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(DiseaseReport.STATUS_CHOICES):
            return Response(
                {"error": "Invalid status"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        disease_report.status = new_status
        disease_report.save()
        
        serializer = self.get_serializer(disease_report)
        return Response(serializer.data)

@method_decorator(csrf_exempt, name='dispatch')
class ExpertRecommendationViewSet(viewsets.ModelViewSet):
    serializer_class = ExpertRecommendationSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        user = self.request.user
        
        if user.user_type == 'expert' and user.is_approved:
            return ExpertRecommendation.objects.filter(expert=user)
        elif user.user_type == 'farmer':
            return ExpertRecommendation.objects.filter(
                disease_report__farmer=user
            )
        else:
            return ExpertRecommendation.objects.none()
    
    def perform_create(self, serializer):
        if not (self.request.user.user_type == 'expert' and self.request.user.is_approved):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only approved experts can create recommendations")
        serializer.save(expert=self.request.user)
    
    @action(detail=False, methods=['get'])
    def for_expert(self, request):
        if not (request.user.user_type == 'expert' and request.user.is_approved):
            return Response(
                {"error": "Only approved experts can access this endpoint"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        disease_reports = DiseaseReport.objects.filter(
            Q(status='pending') | Q(status='in_review')
        )
        serializer = DiseaseReportSerializer(disease_reports, many=True)
        return Response(serializer.data)