import uvicorn
from fastapi import FastAPI

from Storage.InfoStorage import InfoStorage
from Utility.Util import UtilityClass
from Service.PaymentService import PaymentService
from Service.IdempotencyLayer import IdempotencyLayer
from Controller.PaymentController import create_router


app = FastAPI(
    title="Idempotency-Gateway"
)

# Wire up dependencies
info_storage = InfoStorage()
utility_class = UtilityClass(info_storage)
payment_service = PaymentService(info_storage, utility_class)
idempotency_layer = IdempotencyLayer(payment_service, info_storage, utility_class)

# Register the router — this is what was missing
router = create_router(idempotency_layer)
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=1,
    )