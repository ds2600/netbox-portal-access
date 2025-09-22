
from django import forms
from django.contrib.contenttypes.models import ContentType
from netbox.forms import NetBoxModelForm
from .models import Portal, VendorRole, AccessAssignment, RoleCategory

class PortalForm(NetBoxModelForm):
    vendor_ct = forms.ModelChoiceField(
        queryset=ContentType.objects.filter(
            app_label__in=["circuits", "tenancy"],
            model__in=["provider", "tenant"],
        ),
        label="Vendor Type",
    )

    vendor_object = forms.ModelChoiceField(
        queryset=Provider.objects.none(),  
        label="Vendor",
        required=True,
    )

    class Meta:
        model = Portal
        fields = ("vendor_ct", "vendor_object", "name", "base_url", "notes")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields.pop("comment", None)

        ct_pk = self.data.get("vendor_ct") or self.initial.get("vendor_ct")
        if ct_pk:
            try:
                ct = ContentType.objects.get(pk=ct_pk)
            except ContentType.DoesNotExist:
                ct = None
        else:
            ct = None

        if ct and ct.app_label == "circuits" and ct.model == "provider":
            self.fields["vendor_object"].queryset = Provider.objects.all()
            self.fields["vendor_object"].label = "Provider"
        elif ct and ct.app_label == "tenancy" and ct.model == "tenant":
            self.fields["vendor_object"].queryset = Tenant.objects.all()
            self.fields["vendor_object"].label = "Tenant"
        else:
            self.fields["vendor_object"].queryset = Provider.objects.none()
            self.fields["vendor_object"].help_text = "Select Vendor Type first."

        if self.instance.pk and self.instance.vendor_id:
            if self.instance.vendor_ct.app_label == "circuits" and self.instance.vendor_ct.model == "provider":
                self.fields["vendor_object"].queryset = Provider.objects.all()
                try:
                    self.initial["vendor_object"] = Provider.objects.get(pk=self.instance.vendor_id)
                except Provider.DoesNotExist:
                    pass
            elif self.instance.vendor_ct.app_label == "tenancy" and self.instance.vendor_ct.model == "tenant":
                self.fields["vendor_object"].queryset = Tenant.objects.all()
                try:
                    self.initial["vendor_object"] = Tenant.objects.get(pk=self.instance.vendor_id)
                except Tenant.DoesNotExist:
                    pass

    def save(self, *args, **kwargs):
        self.instance.vendor_ct = self.cleaned_data["vendor_ct"]
        self.instance.vendor_id = self.cleaned_data["vendor_object"].pk
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

