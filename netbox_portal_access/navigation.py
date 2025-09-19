
from django.conf import settings
from netbox.plugins import PluginMenuItem, PluginMenu, PluginMenuButton
from django.urls import reverse

items = (
        PluginMenuItem(link="plugins:netbox_portal_access:portal_list", link_text="Portals"),
        PluginMenuItem(link="plugins:netbox_portal_access:vendorrole_list", link_text="Vendor Roles"),
        PluginMenuItem(link="plugins:netbox_portal_access:accessassignment_list", link_text="Access Assignments"),
)

menu = PluginMenu(
    label="Portal Access",
    groups=(
        ("Portal Access", items),
    ),
    icon_class="mdi mdi-shield-key"
)

