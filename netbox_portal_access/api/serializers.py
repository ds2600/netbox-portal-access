
from rest_framework import serializers
from ..models import Portal, VendorRole, AccessAssignment

class PortalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portal
        fields = "__all__"

class VendorRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorRole
        fields = "__all__"

class AccessAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessAssignment
        fields = "__all__"
