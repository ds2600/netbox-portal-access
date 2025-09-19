
from netbox.plugins import PluginConfig

class PortalAccessConfig(PluginConfig):
    name = "netbox_portal_access"
    label = "netbox_portal_access"
    verbose_name = "NetBox Portal Access Tracker"
    version = "0.1.0"
    base_url = "portal-access"
    min_version = "4.0.0"
    max_version = "4.4.1"
    required_settings = []
    default_settings = {
        'top_level_menu': True
    }

config = PortalAccessConfig
