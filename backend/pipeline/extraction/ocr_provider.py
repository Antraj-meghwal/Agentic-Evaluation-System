from abc import ABC, abstractmethod


class BaseOCRProvider(ABC):

    @abstractmethod
    def extract_text(
        self,
        image_path: str
    ) -> str:
        pass