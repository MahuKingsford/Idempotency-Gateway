# package: com.bbquantum.idempotencygateway.DTOs
# Equivalent to: PaymentRequest.java

from pydantic import BaseModel


class PaymentRequest(BaseModel):

    amount: float
    currency: str