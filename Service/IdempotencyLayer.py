import time
import threading

from fastapi.responses import JSONResponse

from DTOs.PaymentRequest import PaymentRequest
from DTOs.StoredInfo import StoredInfo
from Storage.InfoStorage import InfoStorage
from Utility.Util import UtilityClass
from Service.PaymentService import PaymentService


class IdempotencyLayer:

    def __init__(
        self,
        payment_service: PaymentService,
        info_storage: InfoStorage,
        utility_class: UtilityClass
    ):
        self.payment_service = payment_service
        self.info_storage = info_storage
        self.utility_class = utility_class
        self._key_locks: dict[str, threading.Lock] = {}   # One lock per idempotency key
        self._meta_lock = threading.Lock()                 # Protects _key_locks dict itself

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def check_request_validity(self, key: str, payment_request: PaymentRequest) -> JSONResponse:

        key_lock = self._get_key_lock(key)

        with key_lock:  # ← equivalent to: synchronized (key.intern())

            # ── Check 1: New key → process the payment ────────────────
            if not self._check_key(key):
                print(f"Checking key: {key}")
                return self.payment_service.process_payment(key, payment_request)

            # ── Check 2: Same key, different body → 409 Conflict ──────
            if not self._check_request_hash(key, payment_request):
                print("Checking hash:")
                return JSONResponse(
                    content="Idempotent request hash mismatch! Key already used",
                    status_code=409
                )

            # ── Check 3: Same key, same body, still in-flight → wait ──
            if self._check_processing_state(key):
                print("Idempotent request processing")
                time.sleep(10)  # Thread.sleep(10000)

            # ── Check 4: Completed → return cached response ───────────
            stored_info: StoredInfo = self.info_storage.get_stored_info(key)
            response = JSONResponse(content=stored_info.response_body, status_code=201)
            response.headers["X-Cache-Hit"] = "true"
            return response

    # ------------------------------------------------------------------
    # Private helpers (equivalent to Java's private methods)
    # ------------------------------------------------------------------

    def _get_key_lock(self, key: str) -> threading.Lock:

        with self._meta_lock:
            if key not in self._key_locks:
                self._key_locks[key] = threading.Lock()
            return self._key_locks[key]

    def _check_key(self, key: str) -> bool:

        return self.info_storage.get_stored_info(key) is not None

    def _check_request_hash(self, key: str, payment_request: PaymentRequest) -> bool:

        stored_info = self.info_storage.get_stored_info(key)
        new_request_hash = self.utility_class.hash_request_body(payment_request)
        return stored_info.request_hash == new_request_hash

    def _check_processing_state(self, key: str) -> bool:

        stored_info = self.info_storage.get_stored_info(key)
        return stored_info.processing
