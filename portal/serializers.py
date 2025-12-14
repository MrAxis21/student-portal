from rest_framework import serializers
from .models import ServiceRequest

class ServiceRequestSerializer(serializers.ModelSerializer):
    student_username = serializers.ReadOnlyField(source='student.username')

    class Meta:
        model = ServiceRequest
        fields = ['id', 'student', 'student_username', 'request_type', 'details', 'status', 'created_at', 'updated_at', 'admin_comment']
        read_only_fields = ['student', 'status', 'admin_comment']  # Students shouldn't modify status/admin_comment directly via create/update
        
    def create(self, validated_data):
        # Assign current user as student
        validated_data['student'] = self.context['request'].user
        return super().create(validated_data)
