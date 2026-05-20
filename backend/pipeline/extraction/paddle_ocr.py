from paddleocr import PaddleOCR

from pipeline.extraction.ocr_provider import (
    BaseOCRProvider
)


class PaddleOCRProvider(BaseOCRProvider):

    def __init__(self):

        self.ocr = PaddleOCR(
            use_angle_cls=True,
            lang="en"
        )

    def extract_text(
        self,
        image_path: str
    ) -> str:

        results = self.ocr.ocr(image_path)

        extracted_lines = []

        if not results:
            return ""

        for block in results:

            if not block:
                continue

            for line in block:

                text = line[1][0]

                extracted_lines.append(text)

        return "\n".join(extracted_lines)