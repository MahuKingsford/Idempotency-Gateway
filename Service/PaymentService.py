# package: com.bbquantum.idempotencygateway.Service
# Equivalent to: PaymentService.java

import time

from fastapi.responses import JSONResponse

from DTOs.PaymentRequest import PaymentRequest
from DTOs.StoredInfo import StoredInfo
from Storage.InfoStorage import InfoStorage
from Utility.Util import UtilityClass


class PaymentService:


    def __init__(self, info_storage: InfoStorage, utility_class: UtilityClass):
        self.info_storage = info_storage
        self.utility_class = utility_class

    def process_payment(self, key: str, payment_request: PaymentRequest) -> JSONResponse:

        request_hash = self.utility_class.hash_request_body(payment_request)

        stored_response = f"Charged {payment_request.amount} {payment_request.currency}"

        new_info = StoredInfo(
            request_hash=request_hash,
            response_body=stored_response,
            status_code="201",
            processing=True          # Mark as in-flight immediately
        )

        self.info_storage.set_stored_info(key, new_info)  # Store before sleeping so concurrent threads see the key

        time.sleep(2)  # Simulate payment gateway delay — Thread.sleep(2000)

        new_info.set_processing(False)  # Signal that processing is complete

        return JSONResponse(content=stored_response, status_code=201)
