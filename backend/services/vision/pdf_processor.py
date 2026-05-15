# PDF → image conversion
from pdf2image import convert_from_path

# File utilities
import os


# -----------------------------------
# Convert PDF pages into images
# -----------------------------------
def convert_pdf_to_images(

    pdf_path: str,

    output_folder: str
):

    # Convert PDF pages
    pages = convert_from_path(pdf_path)

    image_paths = []

    # Save each page
    for index, page in enumerate(pages):

        image_path = os.path.join(

            output_folder,

            f"page_{index + 1}.png"
        )

        # Save image
        page.save(
            image_path,
            "PNG"
        )

        image_paths.append(image_path)

    return image_paths