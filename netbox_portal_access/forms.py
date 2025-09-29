from django import forms
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from netbox.forms import NetBoxModelForm
from .models import Portal, VendorRole, AccessAssignment, RoleCategory
from utilities.forms.widgets import DatePicker, APISelect
from .adapters import available_choices

class PortalForm(NetBoxModelForm):
    vendor_ct = forms.ModelChoiceField(
        queryset=ContentType.objects.filter(
            app_label__in=['circuits','tenancy'], 
            model__in=['provider','tenant']),
            label="Vendor Type (Provider or Tenant)",
            required=True
        )
    class Meta:
        model = Portal
        fields = ("vendor_ct", "vendor_id", "name", "base_url", "adapter", "notes")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('comment', None)

        provider_ct = ContentType.objects.get(app_label='circuits', model='provider')
        self.fields["vendor_ct"].widget = forms.HiddenInput()

        if not getattr(self.instance, 'vendor_ct_id', None):
            self.initial['vendor_ct'] = provider_ct
        else:
            self.initial.setdefault("vendor_ct", self.instance.vendor_ct_id)

        self.fields["vendor_id"] = forms.IntegerField(
            required = True,
            label = "Vendor",
            widget=APISelect(api_url='/api/circuits/providers/'),
            help_text="Select the vendor associated with this portal."
        )

        if getattr(self.instance, "pk", None) and getattr(self.instance, "vendor_id", None):
            if getattr(self.instance, "vendor_ct_id", None) == provider_ct.id:
                self.initial.setdefault("vendor_id", self.instance.vendor_id)
 
        ch = [("", "- no API adapter -")] + available_choices(getattr(settings, "PLUGINS_CONFIG", {}))
   
        current = (getattr(self.instance, 'adapter', '')
                   or self.initial.get('adapter')
                   or '')

        existing_values = { v for v, _ in ch }
        if current and current not in existing_values:
            ch.append((current, f"{current} (unconfigured)"))

        self.fields['adapter'] = forms.ChoiceField(
            choices=ch, 
            required=False, 
            label="API Adapter",
            help_text="Select an API adapter if the portal supports API access."
        )


        if not self.is_bound:
            self.initial['adapter'] = current

class VendorRoleForm(NetBoxModelForm):

    class Meta:
        model = VendorRole
        fields = ("portal", "name", "category", "description")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('comment', None)


class AccessAssignmentForm(NetBoxModelForm):

    queue_push_now = forms.BooleanField(
        required=False,
        label="Queue vendor push on save",
        help_text="If checked, the assignment will be pushed to the vendor portal immediately after saving."
    )

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

        req = getattr(self, "request", None)
        if req and not req.user.has_perm("netbox_portal_access.can_push_vendor"):
            self.fields.pop("queue_push_now", None)
            return

        portal = getattr(self.instance, "portal", None) if getattr(self.instance, "pk", None) else None
        if portal and not getattr(portal, "adapter", None):
            self.fields["queue_push_now"].widget.attrs["disabled"] = "disabled"
            self.fields["queue_push_now"].help_text = "This portal does not have an API adapter configured."

