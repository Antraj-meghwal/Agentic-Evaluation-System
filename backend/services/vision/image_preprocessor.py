# OpenCV
import cv2

# NumPy
import numpy as np


# -----------------------------------
# Preprocess image
# -----------------------------------
def preprocess_image(image_path: str):

    # Load image
    image = cv2.imread(image_path)

    # Convert to grayscale
    gray = cv2.cvtColor(

        image,

        cv2.COLOR_BGR2GRAY
    )

    # Noise reduction
    denoised = cv2.GaussianBlur(

        gray,

        (5, 5),

        0
    )

    # Increase contrast
    processed = cv2.adaptiveThreshold(

        denoised,

        255,

        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,

        cv2.THRESH_BINARY,

        11,

        2
    )

    # Overwrite image
    cv2.imwrite(
        image_path,
        processed
    )

    return image_path