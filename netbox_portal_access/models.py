
from django.conf import settings
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from netbox.models import NetBoxModel

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

    class Meta:
        unique_together = [('vendor_ct', 'vendor_id', 'name')]
        ordering = ("name",)

    def __str__(self):
        return f"{self.vendor} – {self.name}"

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

    class Meta:
        indexes = [models.Index(fields=['active', 'last_verified', 'expires_on'])]
        constraints = [
            models.CheckConstraint(
                check=(models.Q(user__isnull=False) | models.Q(contact_id__isnull=False)),
                name="assignment_has_subject"
            ),
        ]
        ordering = ("-active", "portal", "role")

    def __str__(self):
        who = getattr(self.user, "username", None) or str(self.contact) or "Unknown"
        return f"{who} -> {self.portal} ({self.role.name})"
