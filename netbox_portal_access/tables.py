
from netbox.tables import NetBoxTable
from netbox.tables.columns import BooleanColumn
from django_tables2 import Column, DateColumn, TemplateColumn
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
    role = Column(accessor="role__name", verbose_name="Role")
    user = Column() 
    active = BooleanColumn()
    last_verified = DateColumn()
    expires_on = DateColumn()
    needs_push = TemplateColumn(
        verbose_name="Needs Push",
        template_code="""
        {% if record.needs_push %}
          <span class="badge bg-danger text-white">Needs pushed</span>
        {% else %}
          <span class="text-muted">—</span>
        {% endif %}
        """,
        orderable=False,
    )
    class Meta(NetBoxTable.Meta):
        model = AccessAssignment
        fields = ("pk", "user", "portal", "role", "active", "last_verified", "expires_on", "created", "last_updated", "needs_push")
