import time
import threading

from DTOs.PaymentRequest import PaymentRequest
from Storage.InfoStorage import InfoStorage


class UtilityClass:

    EXPIRATION_TIME_MS: int = 3_600_000  # 30 000 ms = 30 seconds (matches Java: private final long EXPIRATION_TIME = 30000)

    def __init__(self, info_storage: InfoStorage):
        self.info_storage = info_storage
        self._schedule_cleanup()  # Start the background cleanup job on instantiation

    # ------------------------------------------------------------------
    # Request hashing
    # ------------------------------------------------------------------

    def hash_request_body(self, payment_request: PaymentRequest) -> str:

        return f"{payment_request.amount} {payment_request.currency}"

    # ------------------------------------------------------------------
    # TTL-Based Key Expiry
    # ------------------------------------------------------------------

    def clean_expired_keys(self) -> None:

        print("Cleaning expired keys")
        now = int(time.time() * 1000)  # System.currentTimeMillis()
        storage_map = self.info_storage.get_storage_map()

        # Collect expired keys first (cannot mutate dict during iteration)
        expired_keys = [
            key for key, info in list(storage_map.items())
            if now - info.created_at > self.EXPIRATION_TIME_MS
        ]

        for key in expired_keys:
            storage_map.pop(key, None)

    def _schedule_cleanup(self) -> None:

        def run() -> None:
            self.clean_expired_keys()
            self._schedule_cleanup()  # Reschedule for the next cycle

        timer = threading.Timer(interval=120.0, function=run)
        timer.daemon = True
        timer.start()
