from django.conf import settings
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.urls import reverse
from netbox.models import NetBoxModel
from .adapters import get as get_adapter
from .secrets import encrypt_json, decrypt_json

class RoleCategory(models.TextChoices):
    PORTAL_ADMIN = "PORTAL_ADMIN", "Portal Admin"
    READ_ONLY    = "READ_ONLY", "Read Only"
    TICKETING    = "TICKETING", "Ticketing"
    ORDERING     = "ORDERING", "Ordering"
    LOA_APPROVER = "LOA_APPROVER", "LOA Approver"
    BILLING      = "BILLING", "Billing"
    REPORTS      = "REPORTS", "Reports"

class Portal(NetBoxModel):
    # Points to either circuits.Provider or tenancy.Tenant (i.e., vendor)
    vendor_ct  = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    vendor_id  = models.PositiveIntegerField()
    vendor     = GenericForeignKey('vendor_ct', 'vendor_id')

    name       = models.CharField(max_length=100)  # e.g., "Equinix Customer Portal"
    base_url   = models.URLField(blank=True)
    notes      = models.TextField(blank=True)

    adapter = models.CharField(max_length=64, blank=True, null=True, help_text="Vendor API adapter slug")
    request_timeout = models.PositiveSmallIntegerField(default=10, help_text="Seconds to wait for API responses")
    request_retries = models.PositiveSmallIntegerField(default=3, help_text="Number of times to retry failed requests")
    ssl_verify = models.BooleanField(default=True, help_text="Verify SSL certificates when connecting to the API")
    last_sync_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = [('vendor_ct', 'vendor_id', 'name')]
        ordering = ("name",)

    def __str__(self):
        return f"{self.vendor} – {self.name}"

    def get_adapter(self):
        if not self.adapter:
            return None
        cls = get_adapter(self.adapter)
        if not cls:
            return None

        cfg = (
            getattr(settings, "PLUGINS_CONFIG", {})
           .get("netbox_portal_access", {})
           .get("adapters", {})
           .get(self.adapter, {})
        )

        creds = self.get_credentials()

        return cls(self, cfg, creds)

    def get_credentials(self) -> dict:
        cred = getattr(self, "credential", None)
        return decrypt_json(cred.data_encrypted) if cred else {}

    def set_credentials(self, data: dict) -> None:
        from .models import PortalCredential
        payload = data or {}
        if hasattr(self, "credential") and self.credential:
            self.credential.data_encrypted = encrypt_json(payload)
            self.credential.save()
        else:
            PortalCredential.objects.create(portal=self, data_encrypted=encrypt_json(payload))

class PortalCredential(NetBoxModel):
    portal = models.OneToOneField(Portal, on_delete=models.CASCADE, related_name='credential')
    data_encrypted = models.TextField()

    last_test_at = models.DateTimeField(null=True, blank=True)
    last_test_status = models.CharField(max_length=20, blank=True)
    last_test_message = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ("-last_updated",)
        
    def __str__(self):
        return f"Credentials for {self.portal}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_portal_access:portal_credentials_edit", args=[self.portal.pk])

class VendorRole(NetBoxModel):
    portal     = models.ForeignKey(Portal, on_delete=models.CASCADE, related_name='roles')
    name       = models.CharField(max_length=100)  # vendor's literal label
    category   = models.CharField(max_length=20, choices=RoleCategory.choices)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = [('portal', 'name')]
        ordering = ("portal", "name")

    def __str__(self):
        return f"{self.portal}: {self.name}"

class AccessAssignment(NetBoxModel):
    # Choose one: link to User (internal employees) or a Contact (via GenericForeignKey).
    PUSH_STATUS_CHOICE = (
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    )
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                   on_delete=models.CASCADE, related_name='portal_access')
    contact_ct = models.ForeignKey(ContentType, null=True, blank=True, on_delete=models.PROTECT)
    contact_id = models.PositiveIntegerField(null=True, blank=True)
    contact    = GenericForeignKey('contact_ct', 'contact_id')

    portal     = models.ForeignKey(Portal, on_delete=models.CASCADE, related_name='assignments')
    role       = models.ForeignKey(VendorRole, on_delete=models.PROTECT, related_name='assignments')

    account_identifier = models.CharField(max_length=100, blank=True)  # e.g., Equinix Org ID, Zayo Account #
    username_on_portal = models.CharField(max_length=150, blank=True)
    active     = models.BooleanField(default=True)
    mfa_type   = models.CharField(max_length=50, blank=True)  # e.g., TOTP, SMS, Duo, Okta
    sso_provider = models.CharField(max_length=50, blank=True)  # e.g., Okta, AzureAD
    last_verified = models.DateField(null=True, blank=True)
    expires_on    = models.DateField(null=True, blank=True)
    notes      = models.TextField(blank=True)

    remote_id = models.CharField(max_length=128, blank=True, null=True, db_index=True)
    last_push_status = models.CharField(
            max_length=10, 
            choices=PUSH_STATUS_CHOICE, 
            blank=True, 
            null=True,
            db_index=True
        )
    last_push_at = models.DateTimeField(null=True, blank=True)
    last_push_message = models.TextField(blank=True, null=True)

    @property
    def needs_push(self) -> bool:
        # Unpushed if never pushed or updated after last push
        from django.utils import timezone
        if not self.last_push_at:
            return True
        last_updated = getattr(self, "last_updated", None)
        return bool(last_updated and last_updated > self.last_push_at)

    class Meta:
        indexes = [models.Index(fields=['active', 'last_verified', 'expires_on'])]
        constraints = [
            models.CheckConstraint(
                check=(models.Q(user__isnull=False) | models.Q(contact_id__isnull=False)),
                name="assignment_has_subject"
            ),
        ]
        ordering = ("-active", "portal", "role")
        permissions = [
                ("can_push_vendor", "Can push to vendor"),
                ("can_sync_vendor", "Can sync from vendor"),
        ]

    def __str__(self):
        who = getattr(self.user, "username", None) or str(self.contact) or "Unknown"
        return f"{who} -> {self.portal} ({self.role.name})"
