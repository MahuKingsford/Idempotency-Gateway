# package: com.bbquantum.idempotencygateway.Controller
# Equivalent to: PaymentController.java

from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse

from DTOs.PaymentRequest import PaymentRequest
from Service.IdempotencyLayer import IdempotencyLayer


class PaymentController:

    def __init__(self, idempotency_layer: IdempotencyLayer):
        self.idempotency_layer = idempotency_layer
        self.router = APIRouter()
        self._register_routes()

    def _register_routes(self) -> None:

        @self.router.post("/process-payment")
        def process_payment(
            payment_request: PaymentRequest,
            idempotency_key: str = Header(..., alias="Idempotency-Key")
        ) -> JSONResponse:

            return self.idempotency_layer.check_request_validity(idempotency_key, payment_request)


def create_router(idempotency_layer: IdempotencyLayer) -> APIRouter:

    controller = PaymentController(idempotency_layer)
    return controller.router
