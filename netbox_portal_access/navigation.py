
from netbox.plugins import PluginMenuItem, PluginMenu, PluginMenuButton
from django.urls import reverse

menu = PluginMenu(
    label="Portal Access",
    groups=(
        ("Portal Access", (
            PluginMenuItem(
                link="plugins:netbox_portal_access:portal_list",
                link_text="Portals",
            ),
            PluginMenuItem(
                link="plugins:netbox_portal_access:vendorrole_list",
                link_text="Vendor Roles",
            ),
            PluginMenuItem(
                link="plugins:netbox_portal_access:accessassignment_list",
                link_text="Access Assignments",
            ),
        )),
    )
)
