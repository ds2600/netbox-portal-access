
from rest_framework import serializers
from ..models import Portal, VendorRole, AccessAssignment, PortalCredential
from netbox.api.serializers import NetBoxModelSerializer, WritableNestedSerializer

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

class NestedPortalSerializer(WritableNestedSerializer):
    class Meta:
        model = Portal
        fields = ('id', 'display')

class PortalCredentialSerializer(NetBoxModelSerializer):
    portal = NestedPortalSerializer()

    class Meta:
        model = PortalCredential
        fields = (
            'id',
            'display',
            'portal',
            'last_test_at',
            'last_test_status',
            'last_test_message',
        )

class NestedPortalCredentialSerializer(WritableNestedSerializer):
    class Meta:
        model = PortalCredential
        fields = ('id', 'display')
