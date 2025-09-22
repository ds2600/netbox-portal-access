from django import forms
from django.contrib.contenttypes.models import ContentType

from circuits.models import Provider
from tenancy.models import Tenant

from netbox.forms import NetBoxModelForm
from utilities.forms.fields import DynamicModelChoiceField
from utilities.forms.widgets import APISelect

from .models import Portal, VendorRole, AccessAssignment, RoleCategory

class PortalForm(NetBoxModelForm):
    vendor_ct = forms.ModelChoiceField(
        queryset=ContentType.objects.filter(
            app_label__in=["circuits", "tenancy"], model__in=["provider", "tenant"]
        ),
        label="Vendor Type",
        required=True,
    )

    # Two explicit dropdowns; server-side we require the one that matches vendor_ct
    provider = DynamicModelChoiceField(
        queryset=Provider.objects.all(),
        required=False,
        label="Provider",
        widget=APISelect(api_url="/api/circuits/providers/"),
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label="Tenant",
        widget=APISelect(api_url="/api/tenancy/tenants/"),
    )

    class Meta:
        model = Portal
        # NOTE: vendor_id is not exposed; we derive it from provider/tenant
        fields = ("vendor_ct", "provider", "tenant", "name", "base_url", "notes")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hide NetBox's optional changelog comment box
        self.fields.pop("comment", None)

        # Figure out which CTs correspond to Provider/Tenant
        try:
            self._provider_ct_pk = ContentType.objects.get(app_label="circuits", model="provider").pk
        except ContentType.DoesNotExist:
            self._provider_ct_pk = None
        try:
            self._tenant_ct_pk = ContentType.objects.get(app_label="tenancy", model="tenant").pk
        except ContentType.DoesNotExist:
            self._tenant_ct_pk = None

        # Determine current selected type (POSTed, initial, or instance)
        ct_pk = (
            self.data.get("vendor_ct")
            or self.initial.get("vendor_ct")
            or getattr(self.instance, "vendor_ct_id", None)
        )

        # Default: both disabled until a type is chosen
        self.fields["provider"].widget.attrs["disabled"] = "disabled"
        self.fields["tenant"].widget.attrs["disabled"] = "disabled"

        if ct_pk:
            # Enable the appropriate field based on the chosen vendor type
            if str(ct_pk) == str(self._provider_ct_pk):
                self.fields["provider"].widget.attrs.pop("disabled", None)
                self.fields["tenant"].widget.attrs["disabled"] = "disabled"
            elif str(ct_pk) == str(self._tenant_ct_pk):
                self.fields["tenant"].widget.attrs.pop("disabled", None)
                self.fields["provider"].widget.attrs["disabled"] = "disabled"

        # Prefill when editing an existing object
        if self.instance.pk and self.instance.vendor_id:
            inst_ct = getattr(self.instance, "vendor_ct_id", None)
            if str(inst_ct) == str(self._provider_ct_pk):
                try:
                    self.initial["provider"] = Provider.objects.get(pk=self.instance.vendor_id)
                except Provider.DoesNotExist:
                    pass
            elif str(inst_ct) == str(self._tenant_ct_pk):
                try:
                    self.initial["tenant"] = Tenant.objects.get(pk=self.instance.vendor_id)
                except Tenant.DoesNotExist:
                    pass

        # Make only the relevant dropdown required (server-side)
        if ct_pk and str(ct_pk) == str(self._provider_ct_pk):
            self.fields["provider"].required = True
            self.fields["tenant"].required = False
        elif ct_pk and str(ct_pk) == str(self._tenant_ct_pk):
            self.fields["tenant"].required = True
            self.fields["provider"].required = False
        else:
            self.fields["provider"].required = False
            self.fields["tenant"].required = False

    def clean(self):
        cleaned = super().clean()
        ct = cleaned.get("vendor_ct")
        provider = cleaned.get("provider")
        tenant = cleaned.get("tenant")

        if not ct:
            # No type chosen: both selections must be empty; form will error if save attempted
            return cleaned

        if ct.app_label == "circuits" and ct.model == "provider":
            if not provider:
                self.add_error("provider", "Select a Provider for the chosen Vendor Type.")
            cleaned["tenant"] = None  # ignore any stale tenant value
        elif ct.app_label == "tenancy" and ct.model == "tenant":
            if not tenant:
                self.add_error("tenant", "Select a Tenant for the chosen Vendor Type.")
            cleaned["provider"] = None  # ignore any stale provider value
        else:
            self.add_error("vendor_ct", "Invalid vendor type selection.")

        return cleaned

    def save(self, *args, **kwargs):
        # Persist the GFK pieces from the appropriate field
        ct = self.cleaned_data.get("vendor_ct")
        self.instance.vendor_ct = ct
        if ct and ct.app_label == "circuits" and ct.model == "provider":
            self.instance.vendor_id = self.cleaned_data["provider"].pk if self.cleaned_data.get("provider") else None
        elif ct and ct.app_label == "tenancy" and ct.model == "tenant":
            self.instance.vendor_id = self.cleaned_data["tenant"].pk if self.cleaned_data.get("tenant") else None
        else:
            self.instance.vendor_id = None
        return super().save(*args, **kwargs)

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('comment', None)

