# src/data/base_loader.py
from abc import ABC, abstractmethod
import pandas as pd
from pathlib import Path
from src.config import DATA_PROCESSED

class BaseDataLayer(ABC):
    def __init__(self, force_reload: bool = False):
        self.force_reload = force_reload
        self._data: pd.DataFrame | None = None

    @property
    @abstractmethod
    def processed_path(self) -> Path:
        """Where this loader saves its cleaned output."""

    @abstractmethod
    def load_raw(self) -> pd.DataFrame:
        """Read from raw source (CSV, URL, API)."""

    @abstractmethod
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply cleaning, filtering, type casting."""

    def load(self) -> pd.DataFrame:
        """
        Main entry point. Returns cleaned DataFrame.
        Uses cached processed file if available.
        """
        if not self.force_reload and self.processed_path.exists():
            print(f"[{self.__class__.__name__}] Loading from cache...")
            self._data = pd.read_parquet(self.processed_path)
            return self._data

        print(f"[{self.__class__.__name__}] Processing raw data...")
        raw = self.load_raw()
        self._data = self.clean_data(raw)
        self._data.to_parquet(self.processed_path, index=False)
        return self._data

    @property
    def data(self) -> pd.DataFrame:
        if self._data is None:
            raise RuntimeError("Call .load() before accessing .data")
        return self._data