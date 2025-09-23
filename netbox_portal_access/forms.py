from django import forms
from django.contrib.contenttypes.models import ContentType
from netbox.forms import NetBoxModelForm
from .models import Portal, VendorRole, AccessAssignment, RoleCategory
from utilities.forms.widgets import DatePicker

class PortalForm(NetBoxModelForm):
    vendor_ct = forms.ModelChoiceField(
        queryset=ContentType.objects.filter(app_label__in=['circuits','tenancy'], model__in=['provider','tenant']),
        label="Vendor Type (Provider or Tenant)"
    )
    class Meta:
        model = Portal
        fields = ("vendor_ct", "vendor_id", "name", "base_url", "notes")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('comment', None)

class VendorRoleForm(NetBoxModelForm):

    class Meta:
        model = VendorRole
        fields = ("portal", "name", "category", "description")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('comment', None)


class AccessAssignmentForm(NetBoxModelForm):
    class Meta:
        model = AccessAssignment
        fields = (
            "user",  # For now we prioritize Users; contact is optional via API/nbshell
            "portal", "role",
            "account_identifier", "username_on_portal",
            "active", "mfa_type", "sso_provider",
            "last_verified", "expires_on", "notes",
        )
        widgets = {
            'last_verified': DatePicker(),
            'expires_on': DatePicker(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('comment', None)

