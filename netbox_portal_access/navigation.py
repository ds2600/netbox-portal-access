from django.conf import settings
from netbox.plugins import PluginMenuItem, PluginMenu, PluginMenuButton
from django.urls import reverse

items = (
        PluginMenuItem(
            link="plugins:netbox_portal_access:portal_list", 
            link_text="Portals",
            permissions=["netbox_portal_access.view_portal"],
        ),
        PluginMenuItem(
            link="plugins:netbox_portal_access:vendorrole_list", 
            link_text="Vendor Roles",
            permissions=["netbox_portal_access.view_vendorrole"],
        ),
        PluginMenuItem(
            link="plugins:netbox_portal_access:accessassignment_list", 
            link_text="Access Assignments",
            permissions=["netbox_portal_access.view_accessassignment"],
        ),
)

menu = PluginMenu(
    label="Portal Access",
    groups=(
        ("Portal Access", items),
    ),
    icon_class="mdi mdi-shield-key"
)

