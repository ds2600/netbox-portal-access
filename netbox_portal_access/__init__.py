from netbox.plugins import PluginConfig

class PortalAccessConfig(PluginConfig):
    name = "netbox_portal_access"
    verbose_name = "NetBox Portal Access"
    description = "A plugin to track vendor portal access in NetBox."
    version = "0.1.0"
    base_url = "portal-access"
    min_version = "4.4.1"
    top_level_menu = True
    required_settings = []
    default_settings = {
        "stale_days": 90,
        "expiring_soon_days": 14,
    }

config = PortalAccessConfig
