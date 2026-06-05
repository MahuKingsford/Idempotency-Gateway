# package: com.bbquantum.idempotencygateway.Storage
# Equivalent to: InfoStorage.java

import threading
from typing import Optional, Dict

from DTOs.StoredInfo import StoredInfo


class InfoStorage:


    def __init__(self):
        self._stored_info: Dict[str, StoredInfo] = {}
        self._lock = threading.RLock()  # Reentrant lock — safe if same thread acquires it twice

    def get_stored_info(self, key: str) -> Optional[StoredInfo]:

        return self._stored_info.get(key)

    def set_stored_info(self, key: str, stored_info: StoredInfo) -> None:

        with self._lock:
            self._stored_info[key] = stored_info

    def get_storage_map(self) -> Dict[str, StoredInfo]:

        return self._stored_info
