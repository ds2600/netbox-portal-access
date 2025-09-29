from django.utils import timezone
from django.db import transaction

def push_assignment(assignment_id: int, action: str = "upsert"):
    """Background job: push one AccessAssignment to its vendor"""
    from .models import AccessAssignment
    obj = AccessAssignment.objects.select_related("portal", "role", "user").get(pk=assignment_id)
    portal = obj.portal
    adapter = portal.get_adapter()
    if not adapter:
        _fail(obj, "No adapter configured on portal.")
        return

    try:
        if action == "create":
            ok, msg, rid = adapter.create_access(obj)
        elif action == "update":
            ok, msg, rid = adapter.update_access(obj)
        elif action == "deactivate":
            ok, msg = adapter.deactivate_access(obj)
            rid = obj.remote_id
        elif action == "delete":
            ok, msg = adapter.delete_access(obj)
            rid = None if ok else obj.remote_id
        else:  # default to upsert
            ok, msg, rid = adapter.upsert_access(obj)

        with transaction.atomic():
            obj.last_push_at = timezone.now()
            obj.last_push_status = "SUCCESS" if ok else "FAILED"
            obj.last_push_message = msg[:4000] if msg else None
            if rid is not None:
                obj.remote_id = rid
            obj.save()

    except Exception as e:
        _fail(obj, f"Exception during push: {e}")

def _fail(object, message: str):
    from django.utils import timezone
    obj.last_push_at = timezone.now()
    obj.last_push_status = "FAILED"
    obj.last_push_message = message[:4000]
    obj.save()

