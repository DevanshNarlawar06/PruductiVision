"""
model_store.py
Thread-safe singleton that holds all trained model artifacts.
Populated once at FastAPI startup.
"""

import threading
from typing import Optional


class ModelStore:
    _data: Optional[dict] = None
    _lock = threading.Lock()

    @classmethod
    def set(cls, data: dict):
        with cls._lock:
            cls._data = data

    @classmethod
    def get(cls) -> dict:
        with cls._lock:
            if cls._data is None:
                raise RuntimeError(
                    "Models not trained yet. Server is still starting up."
                )
            return cls._data

    @classmethod
    def is_ready(cls) -> bool:
        with cls._lock:
            return cls._data is not None
