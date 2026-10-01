import cv2
import numpy as np
from typing import Tuple, Dict, Any

class ImagePreprocessor:
    """
    OpenCV Preprocessing Engine for VokaSight Hardware Inspection.
    Performs contrast enhancement (CLAHE), specular glare reduction, 
    and image normalization prior to AI object detection.
    """

    def __init__(self, clip_limit: float = 2.0, tile_grid_size: Tuple[int, int] = (8, 8)):
        self.clip_limit = clip_limit
        self.tile_grid_size = tile_grid_size
        self.clahe = cv2.createCLAHE(clipLimit=self.clip_limit, tileGridSize=self.tile_grid_size)

    def apply_clahe(self, image: np.ndarray) -> np.ndarray:
        """
        Applies Contrast Limited Adaptive Histogram Equalization (CLAHE)
        on the Luminance (L) channel in LAB color space to preserve color balance.
        """
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        l_clahe = self.clahe.apply(l)
        lab_clahe = cv2.merge((l_clahe, a, b))
        return cv2.cvtColor(lab_clahe, cv2.COLOR_LAB2BGR)

    def reduce_glare(self, image: np.ndarray, threshold: int = 230) -> np.ndarray:
        """
        Detects specular highlights (glare) on shiny solder joints/metals 
        and reduces glare using fast telea inpainting.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Create mask of overexposed bright spots
        _, glare_mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
        
        # Dilate mask slightly to cover glare edges
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        glare_mask = cv2.dilate(glare_mask, kernel, iterations=1)

        # Inpaint glare regions using neighboring color information
        inpainted = cv2.inpaint(image, glare_mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
        return inpainted

    def check_lighting_quality(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Evaluates image lighting conditions to catch extreme failure states
        (too dark or excessive glare).
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        mean_brightness = float(np.mean(gray))
        overexposed_ratio = float(np.sum(gray > 240) / gray.size)
        underexposed_ratio = float(np.sum(gray < 20) / gray.size)

        is_suboptimal = mean_brightness < 40 or mean_brightness > 220 or overexposed_ratio > 0.15

        warning_message = None
        if mean_brightness < 40:
            warning_message = "Image is too dark. Please move to a brighter area."
        elif overexposed_ratio > 0.15:
            warning_message = "Excessive glare detected on board. Please turn off direct flash or adjust camera angle."

        return {
            "mean_brightness": round(mean_brightness, 2),
            "overexposed_ratio": round(overexposed_ratio, 4),
            "underexposed_ratio": round(underexposed_ratio, 4),
            "is_suboptimal": is_suboptimal,
            "warning": warning_message
        }

    def process(self, image: np.ndarray) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Full pre-processing pipeline execution.
        Returns normalized image and quality assessment report.
        """
        quality = self.check_lighting_quality(image)
        
        # 1. Reduce Glare
        deglared = self.reduce_glare(image)
        
        # 2. Enhance Contrast via CLAHE
        enhanced = self.apply_clahe(deglared)
        
        return enhanced, quality
