
from netbox.plugins import PluginConfig

class PortalAccessConfig(PluginConfig):
    name = "netbox_portal_access"
    verbose_name = "NetBox Portal Access Tracker"
    description = "A plugin to track portal access in NetBox."
    version = "0.1.0"
    base_url = "portal-access"
    min_version = "4.0.0"
    top_level_menu = True
    required_settings = []
    default_settings = {}

config = PortalAccessConfig
