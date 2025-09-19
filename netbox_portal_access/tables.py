
from netbox.tables import NetBoxTable
from django_tables2 import Column, BooleanColumn, DateColumn
from .models import Portal, VendorRole, AccessAssignment

class PortalTable(NetBoxTable):
    name = Column(linkify=True)
    vendor = Column(accessor="vendor", verbose_name="Vendor") 
    base_url = Column()
    class Meta(NetBoxTable.Meta):
        model = Portal
        fields = ("pk", "name", "vendor", "base_url", "created", "last_updated")

class VendorRoleTable(NetBoxTable):
    portal = Column(linkify=True)
    name = Column(linkify=True)
    category = Column()
    class Meta(NetBoxTable.Meta):
        model = VendorRole
        fields = ("pk", "portal", "name", "category", "created", "last_updated")

class AccessAssignmentTable(NetBoxTable):
    portal = Column() 
    role = Column()
    user = Column() 
    active = BooleanColumn()
    last_verified = DateColumn()
    expires_on = DateColumn()
    class Meta(NetBoxTable.Meta):
        model = AccessAssignment
        fields = ("pk", "user", "portal", "role", "active", "last_verified", "expires_on", "created", "last_updated")
