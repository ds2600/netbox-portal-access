
from netbox.tables import NetBoxTable, columns
from .models import Portal, VendorRole, AccessAssignment

class PortalTable(NetBoxTable):
    name = columns.Column(linkify=True)
    vendor = columns.TemplateColumn(template_code="{{ record.vendor }}")
    base_url = columns.Column()
    class Meta(NetBoxTable.Meta):
        model = Portal
        fields = ("pk", "name", "vendor", "base_url", "created", "last_updated")

class VendorRoleTable(NetBoxTable):
    portal = columns.Column(linkify=True)
    name = columns.Column(linkify=True)
    category = columns.Column()
    class Meta(NetBoxTable.Meta):
        model = VendorRole
        fields = ("pk", "portal", "name", "category", "created", "last_updated")

class AccessAssignmentTable(NetBoxTable):
    portal = columns.Column(linkify=True)
    role = columns.Column(linkify=True)
    user = columns.Column(linkify=True)
    active = columns.BooleanColumn()
    last_verified = columns.DateColumn()
    expires_on = columns.DateColumn()
    class Meta(NetBoxTable.Meta):
        model = AccessAssignment
        fields = ("pk", "user", "portal", "role", "active", "last_verified", "expires_on", "created", "last_updated")
