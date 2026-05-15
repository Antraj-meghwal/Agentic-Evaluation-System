# File utilities
import os

# PDF processor
from services.vision.pdf_processor import (
    convert_pdf_to_images
)

# Image preprocessing
from services.vision.image_preprocessor import (
    preprocess_image
)


# -----------------------------------
# Prepare uploaded file
# for vision grading
# -----------------------------------
def prepare_document_for_grading(

    file_path: str
):

    # File extension
    extension = os.path.splitext(
        file_path
    )[1].lower()

    processed_images = []

    # -----------------------------------
    # PDF handling
    # -----------------------------------
    if extension == ".pdf":

        output_folder = (
            "processed_pages"
        )

        os.makedirs(
            output_folder,
            exist_ok=True
        )

        # Convert pages to images
        page_images = convert_pdf_to_images(

            file_path,

            output_folder
        )

        # Preprocess pages
        for image_path in page_images:

            processed = preprocess_image(
                image_path
            )

            processed_images.append(
                processed
            )

    # -----------------------------------
    # Image handling
    # -----------------------------------
    else:

        processed = preprocess_image(
            file_path
        )

        processed_images.append(
            processed
        )

    return processed_images