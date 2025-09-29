
from django.urls import path
from . import views

app_name = "netbox_portal_access"

urlpatterns = (
    # Portals
    path("portals/", views.PortalListView.as_view(), name="portal_list"),
    path("portals/add/", views.PortalEditView.as_view(), name="portal_add"),
    path("portals/<int:pk>/", views.PortalView.as_view(), name="portal"),
    path("portals/<int:pk>/edit/", views.PortalEditView.as_view(), name="portal_edit"),
    path("portals/<int:pk>/delete/", views.PortalDeleteView.as_view(), name="portal_delete"),
    path("portals/<int:pk>/credentials/", views.PortalCredentialEditView.as_view(), name="portal_credentials_edit"),
    path("portals/<int:pk>/credentials/test/", views.PortalCredentialTestView.as_view(), name="portal_credentials_test"),

    # Vendor Roles
    path("roles/", views.VendorRoleListView.as_view(), name="vendorrole_list"),
    path("roles/add/", views.VendorRoleEditView.as_view(), name="vendorrole_add"),
    path("roles/<int:pk>/", views.VendorRoleView.as_view(), name="vendorrole"),
    path("roles/<int:pk>/edit/", views.VendorRoleEditView.as_view(), name="vendorrole_edit"),
    path("roles/<int:pk>/delete/", views.VendorRoleDeleteView.as_view(), name="vendorrole_delete"),

    # Access Assignments
    path("assignments/", views.AccessAssignmentListView.as_view(), name="accessassignment_list"),
    path("assignments/add/", views.AccessAssignmentEditView.as_view(), name="accessassignment_add"),
    path("assignments/<int:pk>/", views.AccessAssignmentView.as_view(), name="accessassignment"),
    path("assignments/<int:pk>/edit/", views.AccessAssignmentEditView.as_view(), name="accessassignment_edit"),
    path("assignments/<int:pk>/delete/", views.AccessAssignmentDeleteView.as_view(), name="accessassignment_delete"),
    path("assignments/<int:pk>/queue-push/", views.AccessAssignmentQueuePushView.as_view(), name="accessassignment_queue_push"),
    # Changelogs
    path("portals/<int:pk>/changelog/", views.PortalChangelogView.as_view(), name="portal_changelog"),
    path("roles/<int:pk>/changelog/", views.VendorRoleChangelogView.as_view(), name="vendorrole_changelog"),
    path("assignments/<int:pk>/changelog/", views.AccessAssignmentChangelogView.as_view(), name="accessassignment_changelog"),
)
