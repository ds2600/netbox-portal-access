from django.contrib.contenttypes.models import ContentType
from netbox.plugins import PluginTemplateExtension
from django.urls import reverse
from django_tables2 import RequestConfig
from .models import AccessAssignment, Portal
from .tables import AccessAssignmentTable
from django.utils.safestring import mark_safe

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
            "netbox_portal_access/inc/portal_providers_access_panel.html",
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

class PortalUIExtension(PluginTemplateExtension):
    model = "netbox_portal_access.portal"

    def _get_portal(self):
        obj = self.context.get("object")
        return obj if isinstance(obj, Portal) else None

    def buttons(self):
        request = self.context.get("request")
        portal = self._get_portal()
        if not request or not portal:
            return ""  # never run on other models

        btns = []
        try:
            if request.user.has_perm("netbox_portal_access.change_portalcredential"):
                url = reverse("plugins:netbox_portal_access:portal_credentials_edit", args=[portal.pk])
                btns.append(f'<a href="{url}" class="btn btn-sm btn-primary">Credentials</a>')

            if portal.adapter and request.user.has_perm("netbox_portal_access.can_sync_vendor"):
                url = reverse("plugins:netbox_portal_access:portal_credentials_test", args=[portal.pk])
                btns.append(f'<a href="{url}" class="btn btn-sm btn-outline-secondary">Test Adapter</a>')
        except NoReverseMatch:
            return ""  # if URLs not loaded yet, fail closed

        return mark_safe("".join(btns))

    def left_page(self):
        portal = self._get_portal()
        if not portal:
            return ""
        rows = (
            AccessAssignment.objects
            .filter(portal=portal)
            .select_related("user", "role")
            .order_by("-active", "role__name", "user__username")
        )
        return self.render(
            "netbox_portal_access/inc/portal_access_panel.html",
            extra_context={"portal": portal, "rows": rows},
        )

#    def right_page(self):
#        portal = self._get_portal()
#        if not portal:
#            return ""
#        cred = getattr(portal, "credential", None)  # OneToOne name is 'credential'
#        return self.render(
#            "netbox_portal_access/portal_credentials_panel.html",
#            extra_context={"portal": portal, "cred": cred},
#        )

template_extensions = [ProviderPortalAccess, PortalUIExtension]
