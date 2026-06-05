
import time


class StoredInfo:

    def __init__(
        self,
        request_hash: str,
        response_body: str,
        status_code: str,
        processing: bool
    ):
        self.request_hash: str = request_hash
        self.response_body: str = response_body
        self.status_code: str = status_code
        self.processing: bool = processing
        self.created_at: int = int(time.time() * 1000)  # equivalent to System.currentTimeMillis()

    def set_processing(self, processing: bool) -> None:

        self.processing = processing
        self.created_at = int(time.time() * 1000)
