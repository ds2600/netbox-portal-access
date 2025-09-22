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
    )

    vendor = DynamicModelChoiceField(
        queryset=Provider.objects.all(),        
        required=False,
        label="Vendor",
        widget=APISelect(api_url="/api/circuits/providers/"),  
    )

    class Meta:
        model = Portal
        fields = ("vendor_ct", "vendor", "name", "base_url", "notes")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields.pop("comment", None)

        try:
            provider_ct = ContentType.objects.get(app_label="circuits", model="provider").pk
            tenant_ct = ContentType.objects.get(app_label="tenancy", model="tenant").pk
        except ContentType.DoesNotExist:
            provider_ct = tenant_ct = None

        self.fields["vendor"].widget.attrs["data-provider-ct"] = str(provider_ct or "")
        self.fields["vendor"].widget.attrs["data-tenant-ct"] = str(tenant_ct or "")
        self.fields["vendor"].widget.attrs.setdefault("data-url", "/api/circuits/providers/")

        ct_pk = self.data.get("vendor_ct") or self.initial.get("vendor_ct") or getattr(self.instance, "vendor_ct_id", None)
        if ct_pk:
            self.fields["vendor"].widget.attrs.pop("disabled", None)
            if self.instance.pk and self.instance.vendor_id:
                if str(ct_pk) == str(provider_ct):
                    try:
                        self.initial["vendor"] = Provider.objects.get(pk=self.instance.vendor_id)
                    except Provider.DoesNotExist:
                        pass
                elif str(ct_pk) == str(tenant_ct):
                    try:
                        self.initial["vendor"] = Tenant.objects.get(pk=self.instance.vendor_id)
                    except Tenant.DoesNotExist:
                        pass
        else:
            self.fields["vendor"].widget.attrs["disabled"] = "disabled"

    def clean(self):
        cleaned = super().clean()
        ct = cleaned.get("vendor_ct")
        vendor = cleaned.get("vendor")

        if not ct:
            return cleaned

        if ct.app_label == "circuits" and ct.model == "provider":
            if not vendor or not isinstance(vendor, Provider):
                self.add_error("vendor", "Select a Provider for the chosen Vendor Type.")
        elif ct.app_label == "tenancy" and ct.model == "tenant":
            if not vendor or not isinstance(vendor, Tenant):
                self.add_error("vendor", "Select a Tenant for the chosen Vendor Type.")

        return cleaned

    def save(self, *args, **kwargs):
        ct = self.cleaned_data.get("vendor_ct")
        sel = self.cleaned_data.get("vendor")
        self.instance.vendor_ct = ct
        self.instance.vendor_id = getattr(sel, "pk", None)
        return super().save(*args, **kwargs)

    class Media:
        js = ("netbox_portal_access/portal_form.js",)

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

