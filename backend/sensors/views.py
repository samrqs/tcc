from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions

from .serializers import SensorDataSerializer

class SensorWebhookView(APIView):

    permission_classes = [permissions.IsAuthenticated] 

    def post(self, request, *args, **kwargs):
        serializer = SensorDataSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
