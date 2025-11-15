from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
from .models import Department, User, Patient, ConsultRequest, ConsultComment
from .serializers import (
    DepartmentSerializer, UserSerializer, PatientSerializer,
    ConsultRequestSerializer, ConsultRequestCreateSerializer, ConsultCommentSerializer
)


class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for listing departments"""
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]


class PatientViewSet(viewsets.ModelViewSet):
    """ViewSet for managing patients"""
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['hospital_id', 'name']


class ConsultRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for managing consultation requests"""
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['patient__name', 'patient__hospital_id']
    
    def get_queryset(self):
        user = self.request.user
        queryset = ConsultRequest.objects.all()
        
        # Filter based on query parameters
        role = self.request.query_params.get('role', None)
        status_filter = self.request.query_params.get('status', None)
        
        if role == 'incoming':
            # Show consults where user's department is the target
            queryset = queryset.filter(to_department=user.department)
        elif role == 'outgoing':
            # Show consults created by user or from user's department
            queryset = queryset.filter(from_department=user.department)
        else:
            # Show all consults user has access to (incoming or outgoing)
            queryset = queryset.filter(
                Q(to_department=user.department) | Q(from_department=user.department)
            )
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.select_related(
            'patient', 'from_department', 'to_department', 'requested_by'
        ).prefetch_related('comments')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ConsultRequestCreateSerializer
        return ConsultRequestSerializer
    
    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        """Add a comment to a consultation request"""
        consult = self.get_object()
        message = request.data.get('message', '')
        
        if not message:
            return Response(
                {'error': 'Message is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        comment = ConsultComment.objects.create(
            consult=consult,
            author=request.user,
            message=message
        )
        
        serializer = ConsultCommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """Get all comments for a consultation request"""
        consult = self.get_object()
        comments = consult.comments.all()
        serializer = ConsultCommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Update the status of a consultation request"""
        consult = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(ConsultRequest.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status value'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        consult.status = new_status
        consult.save()
        
        serializer = self.get_serializer(consult)
        return Response(serializer.data)
