import cv2
import numpy as np
from typing import Tuple, Dict, Any

class ImagePreprocessor:
    """
    OpenCV Preprocessing Engine for VokaSight Hardware Inspection.
    Performs contrast enhancement (CLAHE), specular glare reduction,
    lighting quality checks, and PCB structure validation.
    """

    def __init__(self, clip_limit: float = 2.0, tile_grid_size: Tuple[int, int] = (8, 8)):
        self.clip_limit = clip_limit
        self.tile_grid_size = tile_grid_size
        self.clahe = cv2.createCLAHE(clipLimit=self.clip_limit, tileGridSize=self.tile_grid_size)

    def apply_clahe(self, image: np.ndarray) -> np.ndarray:
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        l_clahe = self.clahe.apply(l)
        lab_clahe = cv2.merge((l_clahe, a, b))
        return cv2.cvtColor(lab_clahe, cv2.COLOR_LAB2BGR)

    def reduce_glare(self, image: np.ndarray, threshold: int = 230) -> np.ndarray:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, glare_mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        glare_mask = cv2.dilate(glare_mask, kernel, iterations=1)
        inpainted = cv2.inpaint(image, glare_mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
        return inpainted

    def validate_pcb_structure(self, image: np.ndarray) -> bool:
        """
        Validates if the uploaded image contains valid circuit board / hardware structures 
        (copper traces, solder pads, pins) using Canny edge & contour density analysis.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 30, 100)
        
        edge_density = float(np.sum(edges > 0) / edges.size)
        contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        
        # A valid PCB has noticeable structural contours and edge density
        is_pcb = edge_density >= 0.003 or len(contours) >= 5
        return is_pcb

    def check_lighting_quality(self, image: np.ndarray) -> Dict[str, Any]:
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

        is_pcb = self.validate_pcb_structure(image)
        if not is_pcb and not warning_message:
            warning_message = "PCB / Hardware object not detected. Please upload a clear photo of a circuit board or practicum module."

        return {
            "mean_brightness": round(mean_brightness, 2),
            "overexposed_ratio": round(overexposed_ratio, 4),
            "underexposed_ratio": round(underexposed_ratio, 4),
            "is_suboptimal": is_suboptimal or not is_pcb,
            "is_pcb": is_pcb,
            "warning": warning_message
        }

    def process(self, image: np.ndarray) -> Tuple[np.ndarray, Dict[str, Any]]:
        quality = self.check_lighting_quality(image)
        deglared = self.reduce_glare(image)
        enhanced = self.apply_clahe(deglared)
        return enhanced, quality
