
from netbox.views import generic
from netbox.views.generic import ObjectChangeLogView
from . import models, forms, tables, filters

#
# Portals
#
class PortalView(generic.ObjectView):
    queryset = models.Portal.objects.all()

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

class AccessAssignmentListView(generic.ObjectListView):
    queryset = models.AccessAssignment.objects.all()
    table = tables.AccessAssignmentTable
    filterset = filters.AccessAssignmentFilterSet

class AccessAssignmentEditView(generic.ObjectEditView):
    queryset = models.AccessAssignment.objects.all()
    form = forms.AccessAssignmentForm

class AccessAssignmentDeleteView(generic.ObjectDeleteView):
    queryset = models.AccessAssignment.objects.all()

# 
# Changelog Views
#

class PortalChangelogView(ObjectChangelogView):
    queryset = models.Portal.objects.all()

class VendorRoleChangelogView(ObjectChangelogView):
    queryset = models.VendorRole.objects.all()

class AccessAssignmentChangelogView(ObjectChangelogView):
    queryset = models.AccessAssignment.objects.all()
