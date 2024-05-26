from .models import CustomUser
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.http import JsonResponse
from json import JSONDecodeError
from .serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAdminUser


# from devices.serializers import DeviceSerializer
# from rest_framework.decorators import action

class UserViewSet(viewsets.ViewSet):
    queryset = CustomUser.objects.all()
    parser_classes = [JSONParser]
    # serializer_class = UserSerializer

    def get_permissions(self):
        try:
            if self.action in ['create']:
                return [AllowAny()]
            return [IsAuthenticated()]
        except Exception as e:
            # Log or handle the exception as needed
            return [IsAuthenticated()] 

    def create(self, request):
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                refresh = RefreshToken.for_user(user)
                access = refresh.access_token
                return Response({
                    'user': UserSerializer(user).data,
                    'refresh': str(refresh),
                    'access': str(access),
                }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except JSONDecodeError:
            return JsonResponse({"result": "error", "message": "Json decoding error"}, status=400)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def details(self, request, pk=None):
        try:
            # Authenticate the request using JWTAuthentication
            user, _ = JWTAuthentication().authenticate(request)

            # Check if user is authenticated
            if user is None:
                raise AuthenticationFailed()

            # Serialize and return user details
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except AuthenticationFailed:
            return Response({'error': 'Authentication failed'}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
    
    def list(self, request, pk=None):
        if not request.user.is_superuser:
            raise PermissionDenied("You do not have permission to perform this action.")

        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def update(self, request, pk=None):
        try:
            user = self.request.user
            data = request.data.copy()  # Make a copy of the request data
            password = data.pop('password', None)  # Remove password field if present
            serializer = UserSerializer(user, data=data, partial=True)
            if serializer.is_valid():
                if password:
                    user.set_password(password)  # Hash the password
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)  
        
    def destroy(self, request, pk=None):
        if not request.user.is_superuser:
            raise PermissionDenied("You do not have permission to perform this action.")
        
        try:
            user = CustomUser.objects.get(pk=pk)
            user.delete()
            return JsonResponse({'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'], permission_classes=[IsAdminUser])
    def admin(self, request, pk=None):
        try:
            user = CustomUser.objects.get(pk=pk)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    # @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    # def devices(self, request, pk=None):
    #     try:
    #         user = self.request.user
    #         devices = user.devices.all()
    #         serializer = DeviceSerializer(devices, many=True)
    #         return Response(serializer.data)
    #     except CustomUser.DoesNotExist:
    #         return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    #     except Exception as e:
    #         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
