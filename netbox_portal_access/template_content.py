from django.contrib.contenttypes.models import ContentType
from netbox.plugins import PluginTemplateExtension
from .models import AccessAssignment

class ProviderPortalAccess(PluginTemplateExtension):
    # attaches to Circuits → Provider pages
    model = "circuits.provider"

    def right_page(self):
        # hide if the viewer has no permission to see assignments
        req = self.context["request"]
        if not req.user.has_perm("netbox_portal_access.view_accessassignment"):
            return ""

        provider = self.context["object"]
        ct = ContentType.objects.get_for_model(provider)

        qs = (
            AccessAssignment.objects
            .filter(portal__vendor_ct=ct, portal__vendor_id=provider.pk)
            .select_related("portal", "role", "user")
            .order_by("portal__name", "user__username")
        )

        return self.render(
            "netbox_portal_access/inc/portal_access_panel.html",
            extra_context={"assignments": qs}
        )

class TenantPortalAccess(PluginTemplateExtension):
    # attaches to Tenancy → Tenant pages
    model = "tenancy.tenant"

    def right_page(self):
        req = self.context["request"]
        if not req.user.has_perm("netbox_portal_access.view_accessassignment"):
            return ""

        tenant = self.context["object"]
        ct = ContentType.objects.get_for_model(tenant)

        qs = (
            AccessAssignment.objects
            .filter(portal__vendor_ct=ct, portal__vendor_id=tenant.pk)
            .select_related("portal", "role", "user")
            .order_by("portal__name", "user__username")
        )

        return self.render(
            "netbox_portal_access/inc/portal_access_panel.html",
            extra_context={"assignments": qs}
        )

class UserPortalAccess(PluginTemplateExtension):
    # attaches to Users → <user>
    model = "users.user"

    def right_page(self):
        req = self.context["request"]
        if not req.user.has_perm("netbox_portal_access.view_accessassignment"):
            return ""

        user = self.context["object"]
        qs = (
            AccessAssignment.objects
            .filter(user=user)
            .select_related("portal", "role")
            .order_by("portal__name", "role__name")
        )
        return self.render(
            "netbox_portal_access/inc/portal_access_panel.html",
            extra_context={"assignments": qs},
        )

template_extensions = [ProviderPortalAccess, TenantPortalAccess]
