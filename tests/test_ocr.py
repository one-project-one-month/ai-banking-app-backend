"""
Unit tests for the OCR model.
"""

import os
import sys
import unittest
from licence_ocr.api_endpoint.utils.ocr_model import OCR_Model

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class TestLicenceOCR(unittest.TestCase):
    """Tests for the Licence OCR model."""

    def setUp(self):
        """Set up the OCR model with a test image for liceence."""
        self.ocr_model = OCR_Model("test.jpg")

    def test_preprocess_image_for_licence_ocr(self):
        """Test image preprocessing for licence OCR."""
        gray_img = self.ocr_model.preprocess_image_for_licence_ocr()
        self.assertIsNotNone(gray_img)
        self.assertEqual(len(gray_img.shape), 2)  # Check if the image is grayscale

    def test_licence_ocr_model(self):
        """Test the licence OCR model."""
        gray_img = self.ocr_model.preprocess_image_for_licence_ocr()
        nrc = self.ocr_model.licence_ocr_model(gray_img)
        self.assertIsInstance(nrc, str)
        self.assertRegex(nrc, r"\d{1,2}/[A-Z ]+\(N\)[0-9O]{5,7}")


class TestPassportOCR(unittest.TestCase):
    """Tests for the Passport OCR model for Passport."""

    def setUp(self):
        """Set up the OCR model with a test image for passport."""
        self.ocr_model = OCR_Model("test1.jpeg")

    def test_preprocess_image_for_passport_ocr(self):
        """Test image preprocessing for passport OCR."""
        gray_img = self.ocr_model.preprocess_image_for_passport_ocr()
        self.assertIsNotNone(gray_img)
        self.assertEqual(len(gray_img.shape), 2)  # Check if the image is grayscale

    def test_passport_ocr_model(self):
        """Test the passport OCR model."""
        gray_img = self.ocr_model.preprocess_image_for_passport_ocr()
        passport_number = self.ocr_model.passport_ocr_model(gray_img)
        self.assertIsInstance(passport_number, str)
        self.assertRegex(passport_number, r"\b[A-Z]{1,2}[0-9]{6,8}\b")


if __name__ == "__main__":
    unittest.main()
