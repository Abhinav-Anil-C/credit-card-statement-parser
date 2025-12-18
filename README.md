

## Extracted Data Points

The parser extracts the following fields from each credit card statement:

* **Cardholder Name**
* **Card Last 4 Digits**
* **Statement Period**
* **Total Balance Due**
* **Payment Due Date**


## Supported Statement Types

* Digital (text-based) PDF statements
* Scanned / image-based PDF statements (OCR fallback)


## Tech Stack & Libraries Used

* **Python 3.9+**
* **pdfplumber** – Extracts text from digital PDFs
* **PyMuPDF (fitz)** – Renders PDF pages for OCR
* **pytesseract** – OCR engine wrapper
* **Tesseract OCR** – Native OCR executable
* **Pillow (PIL)** – Image preprocessing

  * Grayscale conversion
  * Contrast enhancement
  * Sharpening
* **re** – Regex-based field extraction
* **os, io** – File handling utilities


## How It Works

### Text Extraction

* Attempts text extraction using **pdfplumber**
* Automatically falls back to OCR if no text is detected

### OCR Processing

* PDF pages are rendered using **PyMuPDF**
* Images are preprocessed:

  * Converted to grayscale
  * Contrast is increased
  * Images are sharpened
* OCR is performed using **Tesseract**

### Field Extraction Logic

* Regex-based matching with line-level heuristics
* Cardholder name detection supports:

  * Prefixes (`Mr`, `Mrs`, `Ms`, `Dr`)
  * Uppercase and mixed-case names
  * Names without prefixes
  * Maximum **3-word name limit**
  * Filtering of address and non-name lines
* Supports **multiple currency formats (₹ / $)**

## Output Example
<img width="1495" height="422" alt="image" src="https://github.com/user-attachments/assets/71069c43-853f-4431-86d6-27f7c5881a17" />




