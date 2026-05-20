from pathlib import Path

import fitz


def crop_answer_region(
    pdf_path: str,
    page_number: int,
    bbox_norm: list[float],
    output_path: str,
    dpi: int = 150
):
    """
    Crop a normalized bounding box region from a PDF page
    and save it as PNG.
    """

    pdf_document = fitz.open(pdf_path)

    page = pdf_document[page_number]

    page_rect = page.rect

    x0 = bbox_norm[0] * page_rect.width
    y0 = bbox_norm[1] * page_rect.height
    x1 = bbox_norm[2] * page_rect.width
    y1 = bbox_norm[3] * page_rect.height

    clip_rect = fitz.Rect(x0, y0, x1, y1)

    matrix = fitz.Matrix(dpi / 72, dpi / 72)

    pix = page.get_pixmap(
        matrix=matrix,
        clip=clip_rect
    )

    output_file = Path(output_path)

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    pix.save(output_path)

    pdf_document.close()

    return output_path