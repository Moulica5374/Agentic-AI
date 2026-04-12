"""
OCR Tool — extracts text from scanned document images
Uses Google Gemini Vision as primary OCR engine
"""

import os
from PIL import Image
import google.genai as genai


class OCRTool:
    """
    Extracts text from scanned insurance document images
    using Gemini Vision.
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.client = genai.Client(api_key=self.api_key)
        self.model = 'gemini-2.0-flash'

    def extract_text(self, image_path: str) -> dict:
        """
        Extract all text from a scanned document image.

        Args:
            image_path: Path to scanned document image

        Returns:
            dict with extracted text and status
        """
        try:
            image = Image.open(image_path)

            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    image,
                    """Extract ALL text from this scanned document 
                    exactly as it appears. Include all numbers, 
                    codes, IDs, dates, and labels. 
                    Return raw extracted text only."""
                ]
            )

            return {
                'image_path': image_path,
                'extracted_text': response.text,
                'status': 'success',
                'error': None
            }

        except Exception as e:
            return {
                'image_path': image_path,
                'extracted_text': None,
                'status': 'error',
                'error': str(e)
            }

    def extract_ids(self, image_path: str, insurance_type: str) -> dict:
        """
        Extract and classify IDs from a scanned document.

        Args:
            image_path: Path to scanned document image
            insurance_type: Type of insurance document

        Returns:
            dict with PRIMARY and SECONDARY IDs
        """
        try:
            image = Image.open(image_path)

            prompt = f"""
            This is a scanned {insurance_type} insurance document.
            
            Find ALL ID numbers, reference codes, and identifiers.
            
            For each ID found, classify it as:
            - PRIMARY: The main identifier for this document
              (claim number, policy number, document ID)
            - SECONDARY: Supporting reference IDs
              (registration number, tax ID, reference code)
            
            Return ONLY in this exact format:
            PRIMARY: <value>
            SECONDARY: <value>
            SECONDARY: <value>
            """

            response = self.client.models.generate_content(
                model=self.model,
                contents=[image, prompt]
            )

            return {
                'image_path': image_path,
                'insurance_type': insurance_type,
                'raw_response': response.text,
                'status': 'success',
                'error': None
            }

        except Exception as e:
            return {
                'image_path': image_path,
                'insurance_type': insurance_type,
                'raw_response': None,
                'status': 'error',
                'error': str(e)
            }


if __name__ == '__main__':
    print('OCR Tool initialized!')
    print('Usage: OCRTool(api_key).extract_ids(image_path, insurance_type)')
