import pdfplumber
import pytesseract
from PIL import Image
import re

def extract_text_from_pdf(file_path):
    """Extracts text from all pages of a PDF file."""
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def extract_text_from_image(image_file):
    """Extracts text from an image file using Tesseract OCR."""
    image = Image.open(image_file)
    text = pytesseract.image_to_string(image)
    return text

def extract_details_with_regex(text):
    """Extracts invoice details using regular expressions."""
    
    # Define regex patterns for each field you need
    patterns = {
        'Invoice Number': r'(?:Invoice No|Bill No|SRN)\.?\s*:?\s*([A-Z0-9-]+)',
        'Invoice Date': r'(?:Issue Date|Date)\s*:\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
        'IRN': r'IRN\s*:\s*(\S+)',
        'Buyer GSTIN': r'GSTIN\s*:\s*([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1})',
        'Buyer Name': r'Bill to Ship to\s*\n(.*?)\n',
        'Total Amount': r'(?:TOTAL|Amount Payable|Grand Total)\s*:?\s*[\S]?\s*([\d,]+\.?\d{0,2})'
    }

    # Dictionary to hold the extracted information
    extracted_data = {}

    # Loop through patterns, search the text, and store the findings
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            extracted_data[key] = match.group(1).strip()
        else:
            extracted_data[key] = "Not Found"
            
    # A special check for Buyer GSTIN as it might belong to the seller
    # This is a simple example; more complex logic may be needed
    bill_to_section = re.search(r'Bill to(.*?)Ship to', text, re.DOTALL | re.IGNORECASE)
    if bill_to_section:
        buyer_gst_match = re.search(r'GSTIN\s*:\s*(\S+)', bill_to_section.group(1))
        if buyer_gst_match:
            extracted_data['Buyer GSTIN'] = buyer_gst_match.group(1).strip()

    return extracted_data