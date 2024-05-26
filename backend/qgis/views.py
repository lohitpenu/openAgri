from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import QGIS, Device
from .serializers import QGISSerializer
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser

QGIS_DEV = 2

class QGISViewSet(viewsets.ModelViewSet):
    queryset = QGIS.objects.all()
    serializer_class = QGISSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        device_id = request.data.get('device')
        try:
            device = Device.objects.get(id=device_id)
        except Device.DoesNotExist:
            return Response({'error': 'Device not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if device.type.id != QGIS_DEV:
            return Response({'error': 'Device is not of type QGIS'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the device is associated with the authenticated user
        if not request.user.is_superuser and request.user not in device.users.all():
            return Response({'error': 'Device is not associated with the authenticated user'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='by-location')
    def by_location(self, request):
        lat = request.query_params.get('lat')
        long = request.query_params.get('long')

        if not lat or not long:
            return Response({'error': 'Latitude and longitude are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            lat = float(lat)
            long = float(long)
        except ValueError:
            return Response({'error': 'Invalid latitude or longitude'}, status=status.HTTP_400_BAD_REQUEST)

        qgis_data = QGIS.objects.filter(geo_location_lat=lat, geo_location_long=long, device__users=request.user)

        serializer = QGISSerializer(qgis_data, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-location/admin', permission_classes=[IsAdminUser])
    def by_location_admin(self, request):
        lat = request.query_params.get('lat')
        long = request.query_params.get('long')

        if not lat or not long:
            return Response({'error': 'Latitude and longitude are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            lat = float(lat)
            long = float(long)
        except ValueError:
            return Response({'error': 'Invalid latitude or longitude'}, status=status.HTTP_400_BAD_REQUEST)

        qgis_data = QGIS.objects.filter(geo_location_lat=lat, geo_location_long=long)

        serializer = QGISSerializer(qgis_data, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='mapped-to-user')
    def mapped_to_user(self, request):
        qgis_data = QGIS.objects.filter(device__users=request.user)

        serializer = QGISSerializer(qgis_data, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='mapped-to-user/admin')
    def mapped_to_any_user(self, request):
        user_id = request.query_params.get('user_id')

        if not user_id:
            return Response({'error': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        if not request.user.is_superuser:
            return Response({'error': 'Only admin users can access this endpoint'}, status=status.HTTP_403_FORBIDDEN)

        qgis_data = QGIS.objects.filter(device__users__id=user_id)
        serializer = QGISSerializer(qgis_data, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-device')
    def by_device(self, request):
        device_id = request.query_params.get('device_id')

        if not device_id:
            return Response({'error': 'Device ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            device = Device.objects.get(id=device_id)
        except Device.DoesNotExist:
            return Response({'error': 'Device not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if the device is associated with the authenticated user
        if not request.user.is_superuser and request.user not in device.users.all():
            return Response({'error': 'Device is not associated with the authenticated user'}, status=status.HTTP_403_FORBIDDEN)

        qgis_data = QGIS.objects.filter(device=device)

        serializer = QGISSerializer(qgis_data, many=True)
        return Response(serializer.data)

    def update(self, request, pk=None):
        try:
            qgis = self.get_object()
            device = qgis.device

            if device.type.id != QGIS_DEV:
                return Response({'error': 'Device is not of type QGIS'}, status=status.HTTP_400_BAD_REQUEST)

            if not request.user.is_superuser and request.user not in device.users.all():
                return Response({'error': 'Device is not associated with the authenticated user'}, status=status.HTTP_403_FORBIDDEN)

            serializer = self.get_serializer(qgis, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except QGIS.DoesNotExist:
            return Response({'error': 'QGIS data not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)