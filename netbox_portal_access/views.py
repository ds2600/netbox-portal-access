
from netbox.views import generic
from . import models, forms, tables, filters
from django_rq import enqueue
from .tasks import push_assignment
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone

#
# Portals
#
class PortalView(generic.ObjectView):
    queryset = models.Portal.objects.all()
    template_name = "netbox_portal_access/object.html"

class PortalListView(generic.ObjectListView):
    queryset = models.Portal.objects.all()
    table = tables.PortalTable
    filterset = filters.PortalFilterSet

class PortalEditView(generic.ObjectEditView):
    queryset = models.Portal.objects.all()
    form = forms.PortalForm

class PortalDeleteView(generic.ObjectDeleteView):
    queryset = models.Portal.objects.all()

class PortalCredentialEditView(generic.ObjectEditView):
    template_name = "generic/object_edit.html"
    queryset = models.PortalCredential.objects.all()
    form = forms.PortalCredentialForm

    def get_object(self, **kwargs):
        portal = get_object_or_404(models.Portal, pk=kwargs.get("pk"))
        cred = getattr(portal, "credential", None)
        if cred:
            return cred

        return models.PortalCredential(portal=portal, data_encrypted="")

    def get_extra_context(self, request, instance):
        portal = instance.portal
        url = getattr(portal, "get_absolute_url", None)
        return {
            "return_url": url() if callable(url) else reverse("plugins:netbox_portal_access:portal", args=[portal.pk]),
        }

class PortalCredentialTestView(generic.ObjectView):
    queryset = models.Portal.objects.all()

    def get(self, request, *args, **kwargs):
        portal = self.get_object(**kwargs)
        adapter = portal.get_adapter()
        if not adapter:
            messages.error(request, "No adapter configured for this portal.")
            return redirect(portal.get_absolute_url())

        ok = False
        msg = "No response"
        try:
            ok = bool(adapter.ping())
            msg = "OK" if ok else "Failed"
        except Exception as e:
            ok = False
            msg = f"Exception: {e}"

        cred = getattr(portal, "credential", None)
        if cred:
            cred.last_test_at = timezone.now()
            cred.last_test_status = "OK" if ok else "Failed"
            cred.last_test_message = msg
            cred.save()

        if ok:
            messages.success(request, f"Connection test succeeded: {msg}")
        else:
            messages.error(request, f"Connection test failed: {msg}")
        return redirect(portal.get_absolute_url())


#
# Vendor Roles
#
class VendorRoleView(generic.ObjectView):
    queryset = models.VendorRole.objects.all()
    template_name = "netbox_portal_access/object.html"

class VendorRoleListView(generic.ObjectListView):
    queryset = models.VendorRole.objects.all()
    table = tables.VendorRoleTable
    filterset = filters.VendorRoleFilterSet

class VendorRoleEditView(generic.ObjectEditView):
    queryset = models.VendorRole.objects.all()
    form = forms.VendorRoleForm

class VendorRoleDeleteView(generic.ObjectDeleteView):
    queryset = models.VendorRole.objects.all()

#
# Access Assignments
#
class AccessAssignmentView(generic.ObjectView):
    queryset = models.AccessAssignment.objects.all()
    template_name = "netbox_portal_access/object.html"

class AccessAssignmentListView(generic.ObjectListView):
    queryset = models.AccessAssignment.objects.all()
    table = tables.AccessAssignmentTable
    filterset = filters.AccessAssignmentFilterSet

class AccessAssignmentEditView(generic.ObjectEditView):
    queryset = models.AccessAssignment.objects.all()
    form = forms.AccessAssignmentForm

    def form_valid(self, form):
        response = super().form_valid(form)
        if form.cleaned_data.get("queue_push_now") and self.request.user.has_perm("netbox_portal_access.can_push_vendor"):
            enqueue(push_assignment, assignment_id=self.object.pk, action="upsert")
        return response

class AccessAssignmentDeleteView(generic.ObjectDeleteView):
    queryset = models.AccessAssignment.objects.all()

class AccessAssignmentQueuePushView(PermissionRequiredMixin, generic.ObjectView):
    permission_required = "netbox_portal_access.can_push_vendor"
    queryset = models.AccessAssignment.objects.all()

    def get(self, request, *args, **kwargs):
        obj = self.get_object(**kwargs)
        enqueue(push_assignment, assignment_id=obj.pk, action="upsert")
        messages.success(request, f"Queued push of assignment {obj} to vendor portal.")
        return redirect(obj.get_absolute_url())

# 
# Changelog Views
#

class PortalChangelogView(generic.ObjectChangeLogView):
    queryset = models.Portal.objects.all()
    template_name = "netbox_portal_access/portal_changelog.html"

class VendorRoleChangelogView(generic.ObjectChangeLogView):
    queryset = models.VendorRole.objects.all()
    template_name = "netbox_portal_access/portal_changelog.html"

class AccessAssignmentChangelogView(generic.ObjectChangeLogView):
    queryset = models.AccessAssignment.objects.all()
    template_name = "netbox_portal_access/portal_changelog.html"

