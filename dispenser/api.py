from ninja import NinjaAPI
from apis._router.health_router import health_router
api = NinjaAPI(
    title="Dispenser API",
    description="API for Dispenser",
    version="0.0.1",
)

api.add_router("/", health_router, tags=["health"])