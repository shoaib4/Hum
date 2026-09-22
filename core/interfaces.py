from abc import ABC, abstractmethod
import numpy as np


class AudioRecorderInterface(ABC):
    @abstractmethod
    def start_recording(self) -> None: ...

    @abstractmethod
    def stop_recording(self) -> np.ndarray: ...

    @property
    @abstractmethod
    def is_recording(self) -> bool: ...


class SpeechEngineInterface(ABC):
    @abstractmethod
    def start(self) -> bool: ...

    @abstractmethod
    def transcribe(self, audio: np.ndarray) -> str: ...

    @abstractmethod
    def shutdown(self) -> None: ...

    @property
    @abstractmethod
    def is_ready(self) -> bool: ...


class TextInserterInterface(ABC):
    @abstractmethod
    def insert(self, text: str) -> bool: ...

    def copy(self, text: str) -> bool:
        """Put text on the clipboard without delivering it to the focused window.

        Defaults to insert() for backends where insertion is already clipboard-only.
        """
        return self.insert(text)
