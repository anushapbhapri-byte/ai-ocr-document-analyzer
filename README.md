# AI OCR Document Analyzer

An OCR-based invoice processing project that extracts important fields from invoice images, validates the extracted data, checks OCR confidence, and identifies invoices that may need manual review.

The project uses Tesseract OCR and OpenCV for image processing, along with Python-based extraction, validation, benchmarking, and reporting.

---

## Project Overview

The main goal of this project is to build a complete invoice OCR workflow rather than just extracting text from an image.

The pipeline takes an invoice image, preprocesses it, performs OCR, extracts the required fields, validates the results, and then decides whether the output can be accepted automatically or should be reviewed manually.

**Workflow:**

Invoice Image → Image Preprocessing → Tesseract OCR → Field Extraction → Normalization & Validation → Confidence Analysis → Review Decision → CSV / Excel Output

---

## Key Results

The project was evaluated using a benchmark of 50 invoice images and corresponding noisy versions.

| Metric | Result |
|---|---:|
| Field Accuracy | **94.75%** |
| Character Accuracy | **95.06%** |
| Benchmark Invoices | **50** |
| Processing Errors | **0** |
| Straight-Through Processing | **74.00%** |
| Average Processing Time | **4.426 sec/invoice** |

> These results are based on the current benchmark dataset and configuration. Performance can vary for invoices with different layouts, image quality, or field formats.

---

## Features

- Invoice image preprocessing using OpenCV
- OCR using Tesseract
- Extraction of structured invoice fields
- Field normalization
- Rule-based validation
- OCR confidence analysis
- Comparison of different preprocessing methods
- Benchmark evaluation
- Field-level error analysis
- Batch invoice processing
- Manual-review routing
- CSV and Excel report generation
- Tkinter-based desktop application
- Automated tests using pytest

---

## Invoice Fields

The system extracts the following fields:

- Invoice Number
- Invoice Date
- Seller Tax ID
- Client Tax ID
- Seller IBAN
- Net Worth
- VAT
- Gross Worth

---

## How the OCR Pipeline Works

### 1. Image Preprocessing

Invoice images can contain noise, uneven lighting, or other image-quality issues that affect OCR.

The project compares several preprocessing approaches:

- Original
- Grayscale
- Threshold
- Adaptive threshold
- Denoising
- Resize
- Sharpening

The different preprocessing methods are evaluated using the same benchmark dataset.

### 2. OCR

Tesseract OCR is used to convert the processed invoice image into text.

The Python application communicates with Tesseract through `pytesseract`.

### 3. Field Extraction

The extracted OCR text is processed to identify the required invoice fields.

Different extraction and normalization rules are used depending on the field.

### 4. Validation

The extracted values are checked against expected formats and basic validation rules.

Examples include:

- Invoice number format
- Date format
- Tax ID format
- IBAN format
- Numeric amount validation
- VAT validation

### 5. Confidence Analysis

Tesseract provides confidence information for recognized words.

This information is used as one of the signals for identifying potentially unreliable OCR results.

OCR confidence is not treated as factual accuracy. A value can have high OCR confidence and still be incorrect, so benchmark accuracy is evaluated separately against manually verified ground truth.

---

## Benchmark Evaluation

The benchmark uses:

- 50 clean invoice images
- 50 corresponding noisy invoice images
- A manually verified ground-truth CSV

The noisy images are used to test how the OCR pipeline performs when image quality is degraded.

### Preprocessing Comparison

| Metric | Original | Threshold |
|---|---:|---:|
| Field Accuracy | 91.25% | **94.75%** |
| Character Accuracy | 92.30% | **95.06%** |
| Manual-Review Proxy | 8.75% | **5.25%** |

Threshold preprocessing gave the best overall field accuracy on this benchmark.

Compared with the original images, it resulted in:

- **+3.50 percentage points** in field accuracy
- **+2.76 percentage points** in character accuracy
- **−3.50 percentage points** in the manual-review proxy

---

## Field-Level Results

The benchmark also showed that preprocessing affects different fields differently.

| Field | Original | Threshold |
|---|---:|---:|
| Invoice Number | 98% | **100%** |
| Invoice Date | 98% | 96% |
| Seller Tax ID | 96% | 94% |
| Client Tax ID | 92% | 92% |
| Seller IBAN | 78% | 76% |
| Net Worth | 90% | **100%** |
| VAT | 90% | **100%** |
| Gross Worth | 88% | **100%** |

One of the main observations from the benchmark was that amount fields performed well with threshold preprocessing, while fields such as Seller IBAN were more difficult to extract reliably.

---

## Error Analysis

The project includes a separate error-analysis step to understand where OCR extraction fails.

Run:

```bash
python error_analysis.py
```

The errors are grouped into categories such as:

- Missing Extraction
- Numeric / Amount Error
- Character / Identifier Error
- Other Field Mismatch

The analysis generates files such as:

```text
outputs/benchmark/error_details.csv
outputs/benchmark/error_category_summary.csv
outputs/benchmark/field_error_summary.csv
```

It also generates visualizations for comparing error categories.

---

## Batch Processing

Multiple invoices can be processed together using the batch processor.

Place the invoice images inside:

```text
data/batch_invoices/
```

Then run:

```bash
python batch_processor.py
```

The batch process reports:

- Total invoices
- Automatically accepted invoices
- Manual-review invoices
- Processing errors
- Straight-through processing rate
- Manual-review rate
- Average processing time

The results are saved as:

```text
outputs/batch/batch_invoice_results.csv
outputs/batch/batch_invoice_results.xlsx
```

### Batch Results

For the current 50-invoice batch:

| Metric | Result |
|---|---:|
| Total invoices | 50 |
| Auto accepted | 37 |
| Manual review | 13 |
| Processing errors | **0** |
| Straight-through rate | **74.00%** |
| Manual-review rate | 26.00% |
| Average processing time | 4.426 sec/invoice |

The straight-through rate is based on the current dataset and review rules.

---

## Desktop Application

A Tkinter-based desktop interface is included in the project.

Run:

```bash
python gui_app.py
```

The application allows you to:

- Select an invoice image
- View the image
- Run OCR
- Apply preprocessing
- Extract invoice fields
- View validation results
- View confidence information
- Save results
- Export results to Excel

---

## Project Structure

```text
ai-ocr-document-analyzer/
│
├── data/
│   ├── benchmark/
│   │   ├── images/
│   │   ├── noisy_images/
│   │   └── ground_truth.csv
│   │
│   └── batch_invoices/
│
├── outputs/
│   ├── benchmark/
│   └── batch/
│
├── tests/
│   └── test_project.py
│
├── analytics.py
├── batch_processor.py
├── benchmark_evaluation.py
├── confidence_engine.py
├── create_ground_truth.py
├── dashboard.py
├── data_extractor.py
├── error_analysis.py
├── graph_engine.py
├── gui_app.py
├── main.py
├── ocr_engine.py
├── preprocess.py
├── validation_engine.py
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Tesseract OCR | OCR engine |
| pytesseract | Python interface for Tesseract |
| OpenCV | Image preprocessing |
| NumPy | Image and numerical processing |
| Pillow | Image handling |
| Tkinter | Desktop application |
| OpenPyXL | Excel output |
| Matplotlib | Charts and benchmark visualizations |
| pytest | Testing |

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/anushapbhapri-byte/ai-ocr-document-analyzer.git
cd ai-ocr-document-analyzer
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

On Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install the Python dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Install Tesseract OCR

Tesseract needs to be installed separately because it is an external OCR dependency.

Check the installation with:

```bash
tesseract --version
```

If Tesseract is not available through PATH, the executable can be configured using the `TESSERACT_CMD` environment variable.

Example:

```powershell
$env:TESSERACT_CMD="C:\Path\To\tesseract.exe"
```

---

## Running the Project

### Main OCR application

```bash
python main.py
```

### Desktop application

```bash
python gui_app.py
```

### Batch processing

```bash
python batch_processor.py
```

### Error analysis

```bash
python error_analysis.py
```

### Benchmark evaluation

```bash
python benchmark_evaluation.py
```

### Run tests

```bash
python -m pytest
```

---

## Reproducing the Benchmark

The benchmark can be run with:

```bash
python benchmark_evaluation.py
```

The generated results are saved under:

```text
outputs/benchmark/
```

Some of the generated files include:

```text
benchmark_comparison.csv
detailed_field_results.csv
field_comparison.csv
method_comparison.csv
```

---

## Testing

The project includes automated tests using `pytest`.

The tests cover parts of the project including:

- Image preprocessing
- Field normalization
- Invoice number extraction
- Invoice validation
- Amount validation
- VAT validation
- OCR confidence handling
- Manual-review logic
- Field extraction
- Benchmark-related utilities

Run all tests with:

```bash
python -m pytest
```

---

## Limitations

This project was evaluated using a controlled invoice dataset, so the reported benchmark numbers should not be considered universal OCR performance.

Some current limitations are:

- Invoice layouts can vary significantly between documents.
- OCR performance depends on image quality.
- Some fields are more difficult to extract than others.
- Seller IBAN extraction is currently one of the weaker areas.
- The manual-review percentage is based on the project's review rules and is not a direct measurement of human labor savings.
- Tesseract confidence should not be treated as factual accuracy.
- Tesseract must be installed separately.

---

## Future Improvements

Some areas I would like to improve further are:

- Better extraction of difficult fields such as IBAN
- More robust preprocessing for different invoice qualities
- Support for more invoice layouts
- Testing on a larger and more diverse dataset
- Field-specific confidence thresholds
- Improved review dashboard
- Support for additional document types
- Evaluation using more advanced document understanding models

---

## What I Learned

This project helped me understand that an OCR application involves more than simply extracting text from an image.

The quality of the final structured data depends on several stages:

```text
Image Quality
     ↓
Preprocessing
     ↓
OCR
     ↓
Field Extraction
     ↓
Normalization
     ↓
Validation
     ↓
Confidence Analysis
     ↓
Review Decision
     ↓
Evaluation
```

One of the most useful parts of the project was comparing preprocessing methods using the same benchmark dataset. It made it possible to measure which approach actually improved the results instead of assuming that a preprocessing technique would work better.

---

## Dataset

The benchmark images were sourced from the Kaggle dataset:

**High Quality Invoice Images for OCR**

https://www.kaggle.com/datasets/osamahosamabdellatif/high-quality-invoice-images-for-ocr

For this project, 50 invoices were selected from the dataset.

Clean invoice images were used as reference documents, and noisy versions were created for evaluating OCR performance under degraded image conditions.

The ground-truth values were created from the clean invoice images and manually verified before evaluation.

---

## Project Focus

This project focuses on building an end-to-end OCR and intelligent document-processing workflow around an existing OCR engine.

I did not train a new OCR model from scratch. Instead, I worked on the application side of the problem:

- Image preprocessing
- OCR integration
- Structured field extraction
- Data normalization
- Validation
- Confidence analysis
- Manual-review routing
- Benchmarking
- Error analysis
- Batch processing
- Reporting
- Testing

The main focus was to make the OCR output more useful and measurable for an invoice-processing workflow.

---

## Author

**Anusha Pandurang Bhapri**

[GitHub](https://github.com/anushapbhapri-byte)

---

⭐ If you find the project interesting, feel free to explore the code and benchmark results.
