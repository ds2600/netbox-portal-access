
from netbox.views import generic
from netbox.views.generic import ObjectChangeLogView
from . import models, forms, tables, filters
from django_rq import enqueue
from .tasks import push_assignment
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages

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

class PortalChangelogView(ObjectChangeLogView):
    queryset = models.Portal.objects.all()

class VendorRoleChangelogView(ObjectChangeLogView):
    queryset = models.VendorRole.objects.all()

class AccessAssignmentChangelogView(ObjectChangeLogView):
    queryset = models.AccessAssignment.objects.all()
