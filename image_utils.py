import os
import logging
import numpy as np
from PIL import Image, ExifTags

def extract_exif_data(img: Image.Image) -> dict:
    """
    Extracts EXIF (Exchangeable Image File Format) metadata from a PIL Image object.
    This data can reveal information like the camera used or editing software.
    """
    exif_data = {}
    try:
        # Access the EXIF data from the image.
        exif = img.getexif()
        if exif:
            # Decode the EXIF tags into human-readable names.
            for tag_id, value in exif.items():
                tag = ExifTags.TAGS.get(tag_id, tag_id)
                # Some EXIF data can be very long (like user comments), so we truncate it.
                if isinstance(value, bytes):
                    value = value.decode(errors='ignore')
                if isinstance(value, str) and len(value) > 100:
                    value = value[:100] + '...'
                exif_data[tag] = value
    except Exception as e:
        logging.warning(f"Could not extract EXIF data: {e}")
    return exif_data

def error_level_analysis(img: Image.Image, image_path: str, quality: int = 90) -> float:
    """
    Performs Error Level Analysis (ELA) to detect potential JPEG manipulation.
    The technique involves re-saving a JPEG at a known quality and comparing it to the original.
    Areas with high differences may have been altered. A high overall score suggests manipulation.
    """
    temp_path = f"{image_path}.temp.jpg"
    try:
        # Save the image at a specific JPEG quality.
        img.save(temp_path, "JPEG", quality=quality)
        
        # Re-open the saved image for comparison.
        with Image.open(temp_path) as saved_img:
            # Convert images to numpy arrays for mathematical comparison.
            original_array = np.array(img.convert("RGB")).astype(float)
            saved_array = np.array(saved_img.convert("RGB")).astype(float)
            
            # Calculate the absolute difference between the original and re-saved images.
            diff = np.abs(original_array - saved_array)
            
            # The ELA score is the average difference, scaled for easier interpretation.
            ela_score = np.mean(diff) * 10
            return float(ela_score)
        
    except Exception as e:
        logging.error(f"Error during ELA process: {e}")
        return 0.0
    finally:
        # Ensure the temporary file is always deleted.
        if os.path.exists(temp_path):
            os.remove(temp_path)