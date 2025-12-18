import os
import re
import pdfplumber
import pytesseract
import fitz  # PyMuPDF
import io
from PIL import Image, ImageEnhance, ImageFilter

# Path to Tesseract OCR executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

PDF_FOLDER = r"C:\Users\Abhinav\OneDrive\Documents\Sure Finance\statments"
PDF_FILES = [
    "sample credit card statement 1.pdf",
    "sample credit card statement 2.pdf"
]

# ------------------- Text Extraction -------------------
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def preprocess_image(pix):
    img_bytes = pix.tobytes("ppm")
    img = Image.open(io.BytesIO(img_bytes))
    img = img.convert("L")  # grayscale
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2)
    img = img.filter(ImageFilter.SHARPEN)
    return img

def extract_text_with_ocr(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        pix = page.get_pixmap(dpi=300)
        img = preprocess_image(pix)
        page_text = pytesseract.image_to_string(img)
        text += page_text + "\n"
    return text

# ------------------- Field Extraction -------------------
def extract_fields(text):
    data = {}
    lines = text.splitlines()
    name_found = False

    # --- 1. Cardholder Name ---
    for line in lines[:10]:
        line_clean = line.strip()
        match = re.match(
            r"(?:Name[:\s]*|Cardholder[:\s]*)(Mr\.?|Mrs\.?|Ms\.?|Dr\.?|Mx\.?|)?\s*([A-Za-z\s\-']+)",
            line_clean,
            re.IGNORECASE
        )
        if match:
            prefix = match.group(1) or ""
            name = match.group(2).strip()
            name_parts = name.split()
            if len(name_parts) > 3:
                name = " ".join(name_parts[:3])
            data["cardholder_name"] = (prefix + " " + name).strip()
            name_found = True
            break

    if not name_found:
        for line in lines[:10]:
            match = re.match(
                r"^(Mr\.?|Mrs\.?|Ms\.?|Dr\.?|Mx\.?)\s+([A-Za-z\s\-']+)",
                line.strip(),
                re.IGNORECASE
            )
            if match:
                prefix = match.group(1)
                name = match.group(2).strip()
                name_parts = name.split()
                if len(name_parts) > 3:
                    name = " ".join(name_parts[:3])
                data["cardholder_name"] = (prefix + " " + name).strip()
                name_found = True
                break

    if not name_found:
        data["cardholder_name"] = "Not Found"

    # --- 2. Card Last 4 Digits ---
    acc_match = re.search(
        r"(Account Number|Acct Number|Card Number)[:\s]*[\d\s\-]*?(\d{4})",
        text,
        re.IGNORECASE
    )
    data["card_last_4"] = acc_match.group(2) if acc_match else "Not Found"

    # --- 3. Statement Period ---
    period_match = re.search(
        r"(Opening/Closing Date|Statement Period)[:\s]*([0-9/XX]+\s*[–-]\s*[0-9/XX]+)",
        text,
        re.IGNORECASE
    )
    data["statement_period"] = period_match.group(2) if period_match else "Not Found"

    # --- 4. Total Balance Due (₹ + $ supported) ---
    balance_match = re.search(
        r"(New Balance|Total Balance|Amount Due|Balance Due)[:\s]*[₹$]?\s*([\d,]+\.\d{2})",
        text,
        re.IGNORECASE
    )

    if balance_match:
        data["total_balance"] = balance_match.group(2)
    else:
        # OCR fallback: amount on next line
        data["total_balance"] = "Not Found"
        for i, line in enumerate(lines):
            if re.search(r"(New Balance|Total Balance|Amount Due|Balance Due)", line, re.IGNORECASE):
                if i + 1 < len(lines):
                    amt_match = re.search(r"[₹$]?\s*([\d,]+\.\d{2})", lines[i + 1])
                    if amt_match:
                        data["total_balance"] = amt_match.group(1)
                        break

    # --- 5. Payment Due Date ---
    due_match = re.search(
        r"(Payment Due Date|Due Date|Payment Due)[:\s]*([0-9/XX]+)",
        text,
        re.IGNORECASE
    )
    data["payment_due_date"] = due_match.group(2) if due_match else "Not Found"

    return data

# ------------------- Main Processing -------------------
def process_pdfs():
    for pdf_file in PDF_FILES:
        pdf_path = os.path.join(PDF_FOLDER, pdf_file)
        text = extract_text_from_pdf(pdf_path)

        if not text.strip():
            print(f"\n⚠ No text found in {pdf_file}. Using OCR...")
            text = extract_text_with_ocr(pdf_path)

        extracted_data = extract_fields(text)

        print(f"\n--- Extracted Data from {pdf_file} ---")
        for key, value in extracted_data.items():
            print(f"{key}: {value}")

if __name__ == "__main__":
    process_pdfs()
