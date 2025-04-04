from ninja import Router
import datetime

health_router = Router()

@health_router.get("/health", tags=["System"])
def health_check(request):
    return {
        "status": "ok",
        "timestamp": datetime.datetime.now().isoformat(),
    }
