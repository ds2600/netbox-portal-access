
from netbox.api.routers import NetBoxRouter
from .views import PortalViewSet, VendorRoleViewSet, AccessAssignmentViewSet

router = NetBoxRouter()
router.register("portals", PortalViewSet)
router.register("vendor-roles", VendorRoleViewSet)
router.register("assignments", AccessAssignmentViewSet)

urlpatterns = router.urls
