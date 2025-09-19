
import django_filters
from netbox.filtersets import NetBoxModelFilterSet
from .models import Portal, VendorRole, AccessAssignment, RoleCategory

class PortalFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = Portal
        fields = ['name']

class VendorRoleFilterSet(NetBoxModelFilterSet):
    category = django_filters.CharFilter(field_name='category')
    class Meta:
        model = VendorRole
        fields = ['portal', 'name', 'category']

class AccessAssignmentFilterSet(NetBoxModelFilterSet):
    active = django_filters.BooleanFilter()
    role__category = django_filters.CharFilter(field_name='role__category')
    class Meta:
        model = AccessAssignment
        fields = ['portal', 'role', 'active', 'role__category', 'user']
