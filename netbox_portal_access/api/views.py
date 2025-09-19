
from netbox.api.viewsets import NetBoxModelViewSet
from ..models import Portal, VendorRole, AccessAssignment
from .serializers import PortalSerializer, VendorRoleSerializer, AccessAssignmentSerializer

class PortalViewSet(NetBoxModelViewSet):
    queryset = Portal.objects.all()
    serializer_class = PortalSerializer

class VendorRoleViewSet(NetBoxModelViewSet):
    queryset = VendorRole.objects.all()
    serializer_class = VendorRoleSerializer

class AccessAssignmentViewSet(NetBoxModelViewSet):
    queryset = AccessAssignment.objects.all()
    serializer_class = AccessAssignmentSerializer
