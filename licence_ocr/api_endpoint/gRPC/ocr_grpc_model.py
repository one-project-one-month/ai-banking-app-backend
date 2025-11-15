"""OCR Model for extracting NRC and Passport from images."""

import re

import cv2
import numpy as np
import pytesseract


class OCR_Model:
    """OCR Model for extracting NRC and Passport from images."""

    def __init__(self, image_path: str = None):
        self.image_path = image_path

    def preprocess_image_for_licence_ocr(self):
        """Preprocess the image for better OCR results."""
        if not self.image_path:
            raise ValueError("Image path is not provided.")
        image = cv2.imread(self.image_path)
        brightness = 10
        contrast = 2
        image2 = cv2.addWeighted(
            image, contrast, np.zeros(image.shape, image.dtype), 0, brightness
        )
        gray = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
        return gray

    def licence_ocr_model(self, gray_img):
        """Perform OCR on the preprocessed image."""
        result = pytesseract.image_to_string(gray_img)
        # print(result)

        nrc_pattern = re.compile(r"\d{1,2}/[A-Z ]+\(N\)[0-9O]{5,7}", re.IGNORECASE)

        nrc_match = nrc_pattern.search(result)

        dob_pattern = re.compile(
            r"(?i)\b(?:date of birth|dob|birth date)\b[^0-9]{0,15}"
            r"(\d{1,2}[\/\-.]\d{1,2}[\/\-.]\d{4})"
        )

        dob_match = dob_pattern.search(result)

        data = {}

        if nrc_match:
            nrc = nrc_match.group()
            clean_nrc = re.sub(r"O", "O", nrc)
            clean_nrc = re.sub(r" ", "", clean_nrc)
            data["kyc"] = clean_nrc

        if dob_match:
            dob = dob_match.group(1)
            dob = dob.replace(" ", "")
            for d in ["-", "/", "."]:
                if d in dob:
                    day, month, year = dob.split(d)
                    dob = f"{year}-{month}-{day}"
                break
            data["dateOfBirth"] = dob

        if data:
            return data

        return None

    def preprocess_image_for_passport_ocr(self):
        """Preprocess the image for better OCR results."""
        if not self.image_path:
            raise ValueError("Image path is not provided.")
        image = cv2.imread(self.image_path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return gray

    def passport_ocr_model(self, gray_img):
        """Perform OCR on the preprocessed image."""
        result = pytesseract.image_to_string(gray_img)
        # print(result)

        data = {}

        passport_pattern = r"\b[A-Z]{1,2}[0-9]{6,8}\b"
        matches = re.findall(passport_pattern, result)
        if matches:
            data["kyc"] = matches[0]

        dob_pattern = r"\b(\d{1,2})\s+(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[A-Z]*\s+(\d{4})\b"
        dob_match = re.search(dob_pattern, result, flags=re.IGNORECASE)

        if dob_match:
            day = dob_match.group(1).zfill(2)
            month_str = dob_match.group(2)[:3].upper()
            year = dob_match.group(3)

            month_map = {
                "JAN": "01",
                "FEB": "02",
                "MAR": "03",
                "APR": "04",
                "MAY": "05",
                "JUN": "06",
                "JUL": "07",
                "AUG": "08",
                "SEP": "09",
                "OCT": "10",
                "NOV": "11",
                "DEC": "12",
            }

            month = month_map.get(month_str, "00")
            dob = f"{year}-{month}-{day}"

            data["dateOfBirth"] = dob

        return data if data else None
