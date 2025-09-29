from __future__ import annotations
from typing import Callable, Type

_REGISTERY: dict[str, Type["BaseAdapter"]] = {}

def register(
        slug: str,
        label: str,
        *,
        requires_config: bool = False,
        required_keys: tuple[str, ...] = ()) -> Callable:
    def dec(cls: Type["BaseAdapter"]):
        _REGISTERY[slug] = cls
        cls.slug = slug
        cls.label = label
        cls.requires_config = requires_config
        cls.required_keys = required_keys
        return cls
    return dec

def get(slug: str) -> Type["BaseAdapter"] | None:
    return _REGISTERY[slug]

def all_registered() -> dict[str, Type["BaseAdapter"]]:
    return dict(_REGISTERY)

def available_choices(plugins_config: dict) -> list[tuple[str, str]]:
    """Return [(slug, label)] filtered by PLUGINS_CONFIG presence if required."""
    out: list[tuple[str, str]] = []
    cfg_root = (plugins_config or {}).get("netbox_portal_access", {})
    adapters_cfg = cfg_root.get("adapters", {}) or {}
    for slug, cls in sorted(_REGISTERY.items(), key=lambda x: x[1].label.lower()):
        if getattr(cls, "required_keys", False):
            req = getattr(cls, "required_keys", ()) or ()
            has_all = slug in adpaters_cfg and all(k in adapters_cfg[slug] for k in req)
            if not has_all:
                continue
        out.append((slug, cls.label))
    return out

class BaseAdapter:
    """Adapaters may override any of thse."""
    slug: str = ""
    label: str = ""
    requires_config: bool = False
    required_keys: tuple[str, ...] = ()
    default_base_url: str = ""

    def __init__(self, portal, config: dict, creds: dict | None = None):
        self.portal = portal
        self.config = config or {}
        self.creds = creds or {}
        self.base_url = (self.config.get("base_url") or portal.base_url or self.default_base_url)

        self.timeout = getattr(portal, "request_timeout", 10)
        self.retries = getattr(portal, "request_retries", 3)
        self.verify = getattr(portal, "ssl_verify", True)

    def ping(self) -> bool:
        return True

    # Push CRUDD (Create, Read, Update, Daectivate, Delete)
    def create_access(self, assignment) -> tuple[bool, str, str | None]:
        return False, "Create Not implemented", None
    def read_access(self, assignment) -> tuple[bool, str, dict | None]:
        return False, "Read Not implemented", None
    def update_access(self, assignment) -> tuple[bool, str, str | None]:
        return False, "Update Not implemented", None
    def deactivate_access(self, assignment) -> tuple[bool, str]:
        return False, "Deactivate Not implemented"
    def delete_access(self, assignment) -> tuple[bool, str]:
        return False, "Delete Not implemented"
    def upsert_access(self, assignment) -> tuple[bool, str, str | None]:
        """Default upsert = create if no remote_id, else update."""
        if getattr(assignment, "remote_id", None):
            ok, msg, _ = self.update_access(assignment)
            return ok, msg, assignment.remote_id
        return self.create_access(assignment)

@register("echo", "Demo Echo (httpbingo)", requires_config=True)
class EchoAdapter(BaseAdapter):
    default_base_url = "https://httpbingo.org/post"

    def create_access(self, assignment):
        import requests, json
        payload = {
            "action": "create",
            "assignment_id": assignment.pk,
            "user": getattr(assignment.user, "username", None),
            "portal": assignment.portal.name,
            "role": assignment.role.name if assignment.role else None,
        }
        r = requests.post(self.base_url, json=payload, timeout=self.timeout, verify=self.verify)
        if r.status_code == 200:
            rid = str(hash(json.dumps(payload, sort_keys=True)))
            return True, "Echo OK (create)", rid
        return False, f"Echo failed (create): {r.status_code}", None






            
