from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.hashers import make_password
from .models import Application, User
from .serializers import ApplicationSerializer, UserLoginSerializer, UserSerializer
from .permissions import IsSuperAdmin

class AuthViewSet(viewsets.ViewSet):
    
    permission_classes = [AllowAny] 
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        
        serializer = ApplicationSerializer(data=request.data)
        if serializer.is_valid():
            application = serializer.save()
            return Response({
                "message": "Application submitted successfully. Waiting for admin verification.",
                "application_id": application.id,
                "status": "pending"
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            
            # Get or create authentication token
            token, created = Token.objects.get_or_create(user=user)
            
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data,
                'message': 'Login successful'
            })
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        
        Token.objects.filter(user=request.user).delete()
        return Response({"message": "Logout successful"})
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        
        return Response(UserSerializer(request.user).data)

class AdminViewSet(viewsets.ViewSet):
    
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    
    @action(detail=False, methods=['get'])
    def applications(self, request):
        
        status_filter = request.GET.get('status')
        applications = Application.objects.all()
        
        if status_filter:
            applications = applications.filter(status=status_filter)
        
        serializer = ApplicationSerializer(applications, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        
        application = get_object_or_404(Application, pk=pk)
        
        if application.status == 'verified':
            return Response({"message": "Application already verified"}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        application.status = 'verified'
        application.save()
        
        return Response({"message": "Application verified successfully"})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        
        application = get_object_or_404(Application, pk=pk)
        
        if application.status == 'rejected':
            return Response({"message": "Application already rejected"}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        application.status = 'rejected'
        application.save()
        
        return Response({"message": "Application rejected"})
    
    @action(detail=False, methods=['get'])
    def users(self, request):
       
        role_filter = request.GET.get('role')
        users = User.objects.all()
        
        if role_filter:
            users = users.filter(role=role_filter)
        
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)