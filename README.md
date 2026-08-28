# AI OCR Document Analyzer

I built an OCR-based invoice processing system that converts invoice images into structured, validated data and identifies invoices that may require manual review.

The project combines Tesseract OCR, OpenCV image preprocessing, structured field extraction, validation, confidence analysis, benchmarking, error analysis, and batch processing.

The main goal was not just to extract text from invoices, but to measure how reliable the extracted information is and understand where OCR errors occur.

---

## Why I Built This

Invoice processing often involves manually reading documents, entering information into systems, and verifying extracted values.

I wanted to build a practical system that could automate as much of this process as possible while still keeping human review for cases where the extracted data may not be reliable.

The system was designed to:

- Extract important invoice fields automatically
- Improve OCR results through image preprocessing
- Validate extracted values
- Measure OCR confidence
- Compare OCR results against verified ground truth
- Identify common OCR error patterns
- Automatically accept reliable invoices
- Flag invoices requiring manual review
- Process multiple invoices in batches
- Export results to CSV and Excel

---

## What the System Extracts

The current pipeline extracts structured invoice information including:

- Invoice Number
- Invoice Date
- Seller Tax ID
- Client Tax ID
- Seller IBAN
- Net Worth
- VAT
- Gross Worth

The extracted values go through normalization and validation before the system determines whether the result can be accepted automatically or should be reviewed.

---

## How It Works

```text
Invoice Image
      |
      v
Image Preprocessing
      |
      v
Tesseract OCR
      |
      v
Structured Field Extraction
      |
      v
Field Normalization
      |
      v
Validation + OCR Confidence
      |
      v
Review Decision
      |
      v
CSV / Excel / Analytics
```

I evaluated multiple preprocessing strategies rather than assuming that one preprocessing technique would always perform best.

---

## Image Preprocessing

The benchmark compares seven preprocessing methods:

1. Original
2. Gray
3. Threshold
4. Adaptive
5. Denoise
6. Resize
7. Sharpen

The purpose of this comparison was to determine which preprocessing approach produced the most accurate structured invoice data on the benchmark dataset.

---

# Benchmark

I created a controlled benchmark using:

- 50 clean invoice images
- 50 corresponding noisy invoice images
- A manually verified ground-truth CSV

The ground-truth data was created from the clean invoice images and manually verified before evaluation.

OCR predictions from the noisy images were not used as ground truth.

---

## Evaluation Metrics

### Field Accuracy

Field accuracy uses exact normalized matching between the predicted value and the verified ground-truth value.

For example:

```text
Ground Truth: INV-001
Prediction:   INV-001
Result:       Correct
```

### Character Accuracy

Character accuracy measures similarity between predicted and ground-truth field text.

### Manual-Review Proxy

The project also calculates a manual-review proxy based on incorrect or missing fields.

This is a benchmark metric rather than a measurement of actual human labor time.

---

# Benchmark Results

The current benchmark evaluated all 50 noisy invoices.

|        Metric       | Original |  Threshold |
|---------------------|---------:|-----------:|
| Field Accuracy      |  91.25%  | **94.75%** |
| Character Accuracy  |  92.30%  | **95.06%** |
| Manual-Review Proxy |   8.75%  |  **5.25%** |

### Key results

- Field accuracy improved by **3.50 percentage points**
- Character accuracy improved by **2.76 percentage points**
- Manual-review proxy decreased by **3.50 percentage points**
- Threshold preprocessing achieved the highest overall field accuracy in the benchmark

These results are specific to the controlled benchmark dataset and should not be interpreted as guaranteed performance on arbitrary real-world invoices.

---

## Field-Level Results

The benchmark also helped identify which invoice fields benefit most from preprocessing.

| Field          | Original | Threshold |
|----------------|---------:|----------:|
| Invoice Number |    98%   |  **100%** |
| Invoice Date   |    98%   |     96%   |
| Seller Tax ID  |    96%   |    94%    |
| Client Tax ID  |    92%   |    92%    |
| Seller IBAN    |    78%   |    76%    |
| Net Worth      |    90%   |  **100%** |
| VAT            |    90%   |  **100%** |
| Gross Worth    |    88%   |  **100%** |
| Amount Fields  |  89.33%  |  **100%** |

One of the useful findings was that preprocessing did not improve every field equally.

Threshold preprocessing performed particularly well on monetary fields, while some identifier fields remained more challenging.

---

# Error Analysis

I added a separate error-analysis step to understand why OCR results fail.

Run:

```powershell
python error_analysis.py
```

The analysis categorizes field-level errors into:

- Missing Extraction
- Numeric / Amount Error
- Character / Identifier Error
- Other Field Mismatch

It generates:

```text
outputs/benchmark/error_details.csv
outputs/benchmark/error_category_summary.csv
outputs/benchmark/field_error_summary.csv
outputs/benchmark/error_category_comparison.png
```

This helped move the project beyond simply reporting an accuracy percentage and allowed me to investigate the actual failure modes of the OCR pipeline.

---

# Batch Processing

The project also includes a batch invoice processor.

Invoices can be placed in:

```text
data/batch_invoices/
```

and processed using:

```powershell
python batch_processor.py
```

The processor reports:

- Total invoices
- Automatically accepted invoices
- Manual-review invoices
- Processing errors
- Straight-through processing rate
- Manual-review rate
- Average processing time

Results are exported to:

```text
outputs/batch/batch_invoice_results.csv
outputs/batch/batch_invoice_results.xlsx
```

---

## Current 50-Invoice Batch Run

I tested the batch workflow on all 50 noisy invoices.

Results:

```text
Total invoices          : 50
Auto accepted           : 37
Manual review           : 13
Processing errors       : 0
Straight-through rate   : 74.00%
Manual-review rate      : 26.00%
Average processing time : 4.426 seconds/invoice
```

This demonstrates the end-to-end processing workflow, including automated acceptance and manual-review routing.

The straight-through rate is specific to the current dataset and review rules.

---

# Confidence and Validation

The system keeps OCR confidence separate from factual accuracy.

Tesseract provides word-level confidence, which is useful for identifying potentially uncertain OCR output.

However:

```text
OCR Confidence != Factual Accuracy
```

A value can have high OCR confidence and still be incorrect.

For this reason, the benchmark evaluates predictions independently against manually verified ground truth.

The validation layer also checks whether extracted values follow expected formats and rules.

---

# Desktop Application

The project includes a Tkinter desktop GUI.

Run:

```powershell
python gui_app.py
```

The GUI supports:

- Invoice image upload
- Image viewing
- OCR processing
- Preprocessing comparison
- Structured field extraction
- Validation status
- Confidence information
- Saving results
- Excel export

---

# Running the Project

## 1. Clone the repository

```powershell
git clone <your-repository-url>
cd OCR_Project
```

Replace `<your-repository-url>` with the URL of your GitHub repository.

## 2. Create a virtual environment

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

## 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

## 4. Install Tesseract OCR

Tesseract is an external dependency and must be installed separately.

Verify the installation:

```powershell
tesseract --version
```

If Tesseract is not available through PATH, the project supports configuring the executable through the `TESSERACT_CMD` environment variable.

Example:

```powershell
$env:TESSERACT_CMD="C:\Path\To\tesseract.exe"
```

No machine-specific Tesseract path is hard-coded into the project.

---

# Running the Main Application

For command-line invoice processing:

```powershell
python main.py
```

For the desktop GUI:

```powershell
python gui_app.py
```

---

# Reproducing the Benchmark

The benchmark can be reproduced using:

```powershell
python benchmark_evaluation.py
```

The evaluation uses the 50 noisy invoice images and their manually verified ground-truth records.

The benchmark generates:

```text
outputs/benchmark/
```

including:

```text
benchmark_comparison.csv
detailed_field_results.csv
field_comparison.csv
method_comparison.csv
```

and benchmark graphs.

---

# Running the Tests

The project includes an automated pytest test suite covering core functionality such as:

- Image preprocessing
- Field normalization
- Invoice-number extraction and validation
- Amount and VAT validation
- OCR confidence handling
- Manual-review logic
- Invoice field extraction
- Benchmark utilities

Run:

```powershell
python -m pytest
```

The test suite is included in the repository so the core functionality can be checked from a clean Python environment.

---

# Project Structure

```text
OCR_Project/
|
|-- data/
|   |-- benchmark/
|   |   |-- images/
|   |   |-- noisy_images/
|   |   `-- ground_truth.csv
|   |
|   |-- batch_invoices/
|   `-- invoice.jpg
|
|-- outputs/
|   |-- benchmark/
|   `-- batch/
|
|-- tests/
|   `-- test_project.py
|
|-- analytics.py
|-- batch_processor.py
|-- benchmark_evaluation.py
|-- confidence_engine.py
|-- create_ground_truth.py
|-- data_extractor.py
|-- error_analysis.py
|-- graph_engine.py
|-- gui_app.py
|-- main.py
|-- ocr_engine.py
|-- preprocess.py
|-- validation_engine.py
|
|-- requirements.txt
|-- .gitignore
`-- README.md
```

---

# Technologies Used

- **Python** — application and processing logic
- **Tesseract OCR** — OCR engine
- **pytesseract** — Python interface for Tesseract
- **OpenCV** — image preprocessing
- **NumPy** — numerical/image operations
- **Pillow** — image handling
- **Tkinter** — desktop GUI
- **OpenPyXL** — Excel export
- **Matplotlib** — benchmark visualization
- **pytest** — automated testing

---

# Key Takeaways

Building this project helped me understand that OCR accuracy is not only about the OCR engine itself.

Image quality, preprocessing, field extraction, validation, confidence handling, and downstream business rules all affect the reliability of the final structured data.

The benchmark also showed that improving overall OCR performance does not necessarily mean improving every individual field.

This led me to treat invoice OCR as a combination of:

```text
OCR
+
Data Quality
+
Validation
+
Automation
+
Analytics
```

rather than simply a text-recognition problem.

---

# Known Limitations

This project is currently evaluated on a controlled dataset and is not intended to claim production-level accuracy for arbitrary invoice formats.

Known limitations include:

- Different invoice layouts may produce different results.
- OCR performance depends on image quality and document structure.
- Seller IBAN extraction is currently a weaker area compared with several other fields.
- The manual-review percentage is a benchmark proxy and not a measured labor-time saving.
- Tesseract confidence should not be interpreted as factual accuracy.
- Benchmark results are specific to the current dataset and configuration.
- Tesseract must be installed separately.

These limitations are intentionally documented because reliable evaluation is more important than presenting an inflated performance number.

---

# What I Would Improve Next

The next technical improvement I would focus on is **Seller IBAN extraction**.

The benchmark currently shows that IBAN extraction performs worse than several other invoice fields.

Rather than changing the benchmark or relaxing validation rules simply to increase the score, the goal would be to improve the extraction logic and then rerun the same benchmark to measure whether the improvement is real.

---

# Project Positioning

This is an **AI-assisted intelligent document processing / OCR pipeline**.

I did not train a new OCR model from scratch.

Instead, I built an application layer around an existing OCR engine and focused on making the output more useful for a business workflow through:

- Structured extraction
- Data normalization
- Validation
- OCR confidence analysis
- Manual-review routing
- Preprocessing comparison
- Benchmarking
- Error analysis
- Batch processing
- CSV/Excel reporting
- Automated testing

The focus of the project is applying OCR and AI-assisted automation to a practical document-processing problem.
