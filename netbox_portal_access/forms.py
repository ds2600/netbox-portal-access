from django import forms
from django.contrib.contenttypes.models import ContentType
from netbox.forms import NetBoxModelForm
from circuits.models import Provider
from tenancy.models import Tenant
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
        fields = ("vendor_ct", "provider", "tenant", "name", "base_url", "notes")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop("comment", None)

        if self.instance.pk and self.instance.vendor_id:
            ct = getattr(self.instance, "vendor_ct", None)
            if ct and ct.app_label == "circuits" and ct.model == "provider":
                try:
                    self.initial["provider"] = Provider.objects.get(pk=self.instance.vendor_id)
                except Provider.DoesNotExist:
                    pass
            elif ct and ct.app_label == "tenancy" and ct.model == "tenant":
                try:
                    self.initial["tenant"] = Tenant.objects.get(pk=self.instance.vendor_id)
                except Tenant.DoesNotExist:
                    pass

        ct_pk = self.data.get("vendor_ct") or self.initial.get("vendor_ct")
        if ct_pk:
            try:
                ct = ContentType.objects.get(pk=ct_pk)
            except ContentType.DoesNotExist:
                ct = None
        else:
            ct = None

        if ct and ct.app_label == "circuits" and ct.model == "provider":
            self.fields["provider"].required = True
            self.fields["tenant"].required = False
            self.fields["tenant"].help_text = "Ignored when Vendor Type = Provider."
        elif ct and ct.app_label == "tenancy" and ct.model == "tenant":
            self.fields["tenant"].required = True
            self.fields["provider"].required = False
            self.fields["provider"].help_text = "Ignored when Vendor Type = Tenant."
        else:
            self.fields["provider"].required = False
            self.fields["tenant"].required = False
            self.fields["provider"].help_text = "Select a Vendor Type above."
            self.fields["tenant"].help_text = "Select a Vendor Type above."

    def clean(self):
        cleaned = super().clean()
        ct = cleaned.get("vendor_ct")
        provider = cleaned.get("provider")
        tenant = cleaned.get("tenant")

        if ct and ct.app_label == "circuits" and ct.model == "provider":
            if not provider:
                self.add_error("provider", "Select a Provider for the chosen Vendor Type.")
            cleaned["tenant"] = None
        elif ct and ct.app_label == "tenancy" and ct.model == "tenant":
            if not tenant:
                self.add_error("tenant", "Select a Tenant for the chosen Vendor Type.")
            cleaned["provider"] = None
        return cleaned

    def save(self, *args, **kwargs):
        ct = self.cleaned_data["vendor_ct"]
        self.instance.vendor_ct = ct
        if ct.app_label == "circuits" and ct.model == "provider":
            self.instance.vendor_id = self.cleaned_data["provider"].pk
        else:
            self.instance.vendor_id = self.cleaned_data["tenant"].pk
        return super().save(*args, **kwargs)class VendorRoleForm(NetBoxModelForm):
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

