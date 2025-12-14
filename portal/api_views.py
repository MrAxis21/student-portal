from rest_framework import viewsets, permissions
from .models import ServiceRequest
from .serializers import ServiceRequestSerializer

class ServiceRequestViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return ServiceRequest.objects.all().order_by('-created_at')
        return ServiceRequest.objects.filter(student=user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)
