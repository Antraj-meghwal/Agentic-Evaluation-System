from sqlalchemy.orm import Session

from models.question_crop import (
    CropStatus,
    QuestionCrop
)
from pipeline.extraction.paddle_ocr import (
    PaddleOCRProvider
)


ocr_provider = PaddleOCRProvider()


def run_ocr_pipeline(
    db: Session,
    crop: QuestionCrop
):
    """
    Run OCR extraction for a crop.
    """

    extracted_text = ocr_provider.extract_text(
        crop.crop_image_path
    )

    crop.ocr_text = extracted_text

    crop.status = CropStatus.OCR_COMPLETE

    db.commit()

    db.refresh(crop)

    return crop