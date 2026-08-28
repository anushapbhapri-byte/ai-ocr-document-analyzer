🔎 AI OCR Document Analyzer

Intelligent Invoice Processing, OCR Benchmarking & Document Quality Analysis

An end-to-end OCR-based invoice processing system that converts invoice images into structured, validated data and identifies invoices that may require manual review.

This project combines Tesseract OCR, OpenCV image preprocessing, structured field extraction, validation, confidence analysis, benchmarking, error analysis, and batch processing.

The main goal was not just to extract text from invoices, but to measure how reliable the extracted information is and understand where OCR errors occur.

🎯 Why I Built This

Invoice processing often involves manually reading documents, entering information into systems, and verifying extracted values.

I wanted to build a practical system that could automate as much of this process as possible while still keeping human review for cases where the extracted data may not be reliable.

The system was designed to:

📄 Extract important invoice fields automatically

🖼️ Improve OCR results through image preprocessing

✅ Validate extracted values

📊 Measure OCR confidence

🧪 Compare OCR results against verified ground truth

🔍 Identify common OCR error patterns

🤖 Automatically accept reliable invoices

👥 Flag invoices requiring manual review

📦 Process multiple invoices in batches

📑 Export results to CSV and Excel

📋 What the System Extracts

The current pipeline extracts structured invoice information including:

Invoice Field

Invoice Number

Invoice Date

Seller Tax ID

Client Tax ID

Seller IBAN

Net Worth

VAT

Gross Worth

The extracted values go through normalization and validation before the system determines whether the result can be accepted automatically or should be reviewed.

🔄 How It Works

                    ┌─────────────────────┐
                    │    Invoice Image    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Image Preprocessing │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Tesseract OCR     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Structured Field    │
                    │ Extraction          │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Field Normalization │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Validation + OCR    │
                    │ Confidence          │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   Review Decision   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ CSV / Excel /       │
                    │ Analytics           │
                    └─────────────────────┘

I evaluated multiple preprocessing strategies rather than assuming that one preprocessing technique would always perform best.

🖼️ Image Preprocessing

The benchmark compares seven preprocessing methods:

Original

Gray

Threshold

Adaptive

Denoise

Resize

Sharpen

The purpose of this comparison was to determine which preprocessing approach produced the most accurate structured invoice data on the benchmark dataset.

🧪 Benchmark

I created a controlled benchmark using:

50 clean invoice images

50 corresponding noisy invoice images

A manually verified ground-truth CSV

The ground-truth data was created from the clean invoice images and manually verified before evaluation.

Important: OCR predictions from the noisy images were not used as ground truth.

This provides a controlled way to evaluate how different preprocessing methods affect invoice extraction accuracy.

📊 Evaluation Metrics

Field Accuracy

Field accuracy uses exact normalized matching between the predicted value and the verified ground-truth value.

Example:

Ground Truth: INV-001
Prediction:   INV-001
Result:       Correct

Character Accuracy

Character accuracy measures similarity between predicted and ground-truth field text.

Manual-Review Proxy

The project also calculates a manual-review proxy based on incorrect or missing fields.

This is a benchmark metric rather than a measurement of actual human labor time.

📈 Benchmark Results

The current benchmark evaluated all 50 noisy invoices.

Metric

Original

Threshold

Field Accuracy

91.25%

94.75%

Character Accuracy

92.30%

95.06%

Manual-Review Proxy

8.75%

5.25%

Key Results

📈 Field accuracy improved by 3.50 percentage points

📈 Character accuracy improved by 2.76 percentage points

📉 Manual-review proxy decreased by 3.50 percentage points

🏆 Threshold preprocessing achieved the highest overall field accuracy

These results are specific to the controlled benchmark dataset and should not be interpreted as guaranteed performance on arbitrary real-world invoices.

📋 Field-Level Results

The benchmark also helped identify which invoice fields benefit most from preprocessing.

Field

Original

Threshold

Invoice Number

98%

100%

Invoice Date

98%

96%

Seller Tax ID

96%

94%

Client Tax ID

92%

92%

Seller IBAN

78%

76%

Net Worth

90%

100%

VAT

90%

100%

Gross Worth

88%

100%

Amount Fields

89.33%

100%

Key Observation

Preprocessing did not improve every field equally.

Threshold preprocessing performed particularly well on monetary fields, while some identifier fields remained more challenging.

🔍 Error Analysis

I added a separate error-analysis step to understand why OCR results fail.

Run

python error_analysis.py

The analysis categorizes field-level errors into:

❌ Missing Extraction

🔢 Numeric / Amount Error

🔤 Character / Identifier Error

⚠️ Other Field Mismatch

Generated Outputs

outputs/benchmark/error_details.csv
outputs/benchmark/error_category_summary.csv
outputs/benchmark/field_error_summary.csv
outputs/benchmark/error_category_comparison.png

This moves the project beyond simply reporting an accuracy percentage and allows investigation of the actual failure modes of the OCR pipeline.

📦 Batch Processing

The project also includes a batch invoice processor.

Invoices can be placed in:

data/batch_invoices/

Run

python batch_processor.py

The processor reports:

KPI

Purpose

Total invoices

Total documents processed

Automatically accepted invoices

Documents accepted by the automated workflow

Manual-review invoices

Documents routed for review

Processing errors

Documents that failed processing

Straight-through processing rate

Percentage processed without manual review

Manual-review rate

Percentage requiring review

Average processing time

Average processing time per invoice

Results are exported to:

outputs/batch/batch_invoice_results.csv
outputs/batch/batch_invoice_results.xlsx

📊 Current 50-Invoice Batch Run

I tested the batch workflow on all 50 noisy invoices.

Total invoices          : 50
Auto accepted           : 37
Manual review           : 13
Processing errors       : 0
Straight-through rate   : 74.00%
Manual-review rate      : 26.00%
Average processing time : 4.426 seconds/invoice

Operational Interpretation

The batch workflow demonstrates:

Invoice → OCR → Extraction → Validation → Automated Acceptance / Manual Review

The straight-through rate is specific to the current dataset and review rules.

📊 Confidence & Validation

The system keeps OCR confidence separate from factual accuracy.

Tesseract provides word-level confidence, which is useful for identifying potentially uncertain OCR output.

However:

OCR Confidence ≠ Factual Accuracy

A value can have high OCR confidence and still be incorrect.

For this reason, the benchmark evaluates predictions independently against manually verified ground truth.

The validation layer also checks whether extracted values follow expected formats and rules.

🖥️ Desktop Application

The project includes a Tkinter desktop GUI.

Run

python gui_app.py

The GUI supports:

📤 Invoice image upload

🖼️ Image viewing

🔤 OCR processing

🔄 Preprocessing comparison

📋 Structured field extraction

✅ Validation status

📊 Confidence information

💾 Saving results

📑 Excel export

📈 Analytics & Dashboard

The project includes a dashboard component for presenting OCR benchmark and operational information.

The dashboard is designed around recruiter/business-facing questions such as:

How many invoices were processed?

How many were automatically accepted?

How many required manual review?

Which preprocessing method performed best?

Which invoice fields are most difficult to extract?

What are the major OCR error categories?

How does processing performance vary across the benchmark?

🗃️ Dataset

The project uses synthetic/demo invoice images from the Kaggle dataset:

High Quality Invoice Images for OCR

Kaggle:

https://www.kaggle.com/datasets/osamahosamabdellatif/high-quality-invoice-images-for-ocr

Dataset Selection

For this project:

Source: Batch1_1

Selected images: First 50 invoice images

Clean images: Used to establish the verified reference data

Noisy images: Generated by applying synthetic noise/degradation for OCR evaluation

Kaggle Invoice Dataset
          │
          ▼
       Batch1_1
          │
          ▼
 First 50 Invoice Images
          │
          ├───────────────┐
          │               │
          ▼               ▼
   Clean Reference    Noise / Degradation
          │               │
          │               ▼
          │        50 Noisy Invoices
          │               │
          └───────┬───────┘
                  ▼
          OCR Benchmark
                  │
                  ▼
       Accuracy + Error Analysis

The noisy images were created as part of this project to evaluate OCR robustness under degraded document conditions.

Dataset attribution: The original invoice images come from the Kaggle dataset linked above, and additional synthetic noise/degradation was introduced for this project's evaluation. Please refer to the original dataset page for the applicable license and attribution requirements.

⚙️ Running the Project

1. Clone the repository

git clone <your-repository-url>
cd OCR_Project

Replace <your-repository-url> with the URL of the GitHub repository.

2. Create a virtual environment

python -m venv .venv

Activate it:

.\.venv\Scripts\Activate.ps1

3. Install dependencies

python -m pip install -r requirements.txt

4. Install Tesseract OCR

Tesseract is an external dependency and must be installed separately.

Verify the installation:

tesseract --version

If Tesseract is not available through PATH, configure the executable through the TESSERACT_CMD environment variable.

Example:

$env:TESSERACT_CMD="C:\Path\To\tesseract.exe"

No machine-specific Tesseract path is hard-coded into the project.

▶️ Running the Main Application

Command-line invoice processing

python main.py

Desktop GUI

python gui_app.py

🧪 Reproducing the Benchmark

The benchmark can be reproduced using:

python benchmark_evaluation.py

The evaluation uses the 50 noisy invoice images and their manually verified ground-truth records.

The benchmark generates:

outputs/benchmark/

including:

benchmark_comparison.csv
detailed_field_results.csv
field_comparison.csv
method_comparison.csv

as well as benchmark visualizations.

🔬 Running Error Analysis

After benchmark results have been generated:

python error_analysis.py

This produces:

error_details.csv
error_category_summary.csv
field_error_summary.csv
error_category_comparison.png

inside:

outputs/benchmark/

🧪 Running the Tests

The project includes an automated PyTest test suite covering core functionality such as:

Image preprocessing

Field normalization

Invoice-number extraction and validation

Amount and VAT validation

OCR confidence handling

Manual-review logic

Invoice field extraction

Benchmark utilities

Run:

python -m pytest

The test suite is included in the repository so the core functionality can be checked from a clean Python environment.

📂 Project Structure

OCR_Project/
│
├── data/
│   ├── benchmark/
│   │   ├── images/
│   │   ├── noisy_images/
│   │   └── ground_truth.csv
│   │
│   ├── batch_invoices/
│   └── invoice.jpg
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
├── data_extractor.py
├── dashboard.py
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

🛠️ Technologies Used

Technology

Purpose

Python

Application and processing logic

Tesseract OCR

OCR engine

pytesseract

Python interface for Tesseract

OpenCV

Image preprocessing

NumPy

Numerical and image operations

Pillow

Image handling

Tkinter

Desktop GUI

OpenPyXL

Excel export

Matplotlib

Benchmark visualization

pytest

Automated testing

Git / GitHub

Version control

💼 Business Perspective

The project is designed around a practical operational question:

Can this invoice be processed automatically, or should it be reviewed by a human?

This creates a connection between AI output and business operations.

Instead of treating OCR as simply:

Image → Text

the project evaluates:

Image
  ↓
OCR
  ↓
Structured Data
  ↓
Validation
  ↓
Confidence
  ↓
Business Decision
  ↓
Automated Processing / Manual Review

This makes the project relevant to areas such as:

🧾 Invoice processing

💰 Accounts payable

📄 Document digitization

🔄 Data-entry automation

🤖 Intelligent document processing

📊 Business process analytics

🧠 Key Takeaways

Building this project helped me understand that OCR accuracy is not only about the OCR engine itself.

Image quality, preprocessing, field extraction, validation, confidence handling, and downstream business rules all affect the reliability of the final structured data.

The benchmark also showed that improving overall OCR performance does not necessarily mean improving every individual field.

This led me to treat invoice OCR as a combination of:

OCR
 +
Data Quality
 +
Validation
 +
Automation
 +
Analytics

rather than simply a text-recognition problem.

⚠️ Known Limitations

This project is currently evaluated on a controlled dataset and is not intended to claim production-level accuracy for arbitrary invoice formats.

Known limitations include:

Different invoice layouts may produce different results.

OCR performance depends on image quality and document structure.

Seller IBAN extraction is currently a weaker area compared with several other fields.

The manual-review percentage is a benchmark proxy and not a measured labor-time saving.

Tesseract confidence should not be interpreted as factual accuracy.

Benchmark results are specific to the current dataset and configuration.

Tesseract must be installed separately.

These limitations are intentionally documented because reliable evaluation is more important than presenting an inflated performance number.

🚀 What I Would Improve Next

The next technical improvement I would focus on is:

Seller IBAN Extraction

The benchmark currently shows that IBAN extraction performs worse than several other invoice fields.

Rather than changing the benchmark or relaxing validation rules simply to increase the score, the goal would be to:

Improve the extraction logic

Keep the same benchmark

Rerun the evaluation

Compare the new results against the current baseline

Determine whether the improvement is actually measurable

This keeps the improvement process data-driven and reproducible.

🎯 Project Positioning

This project is an:

AI-assisted Intelligent Document Processing / OCR Pipeline

I did not train a new OCR model from scratch.

Instead, I built an application layer around an existing OCR engine and focused on making its output more useful for a business workflow through:

Structured extraction

Data normalization

Validation

OCR confidence analysis

Manual-review routing

Preprocessing comparison

Benchmarking

Error analysis

Batch processing

CSV / Excel reporting

Automated testing

The focus of the project is applying OCR and AI-assisted automation to a practical document-processing problem.

⭐ Project Highlights

╔══════════════════════════════════════════════════════════╗
║             AI OCR DOCUMENT ANALYZER                     ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  🖼️  Image Preprocessing                                 ║
║  🔤  Tesseract OCR                                       ║
║  📋  Structured Field Extraction                         ║
║  ✅  Validation                                           ║
║  📊  Confidence Analysis                                 ║
║  🧪  Benchmarking                                         ║
║  🔍  Error Analysis                                       ║
║  📦  Batch Processing                                     ║
║  📈  Analytics                                            ║
║  🖥️  Desktop GUI                                         ║
║  👥  Manual-Review Routing                                ║
║  🧪  Automated Testing                                   ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝

👩‍💻 Author

Anusha Bhapri

Computer Science & Engineering
MBA – Artificial Intelligence

📌 Dataset Attribution

Invoice images used in this project were obtained from the Kaggle dataset:

High Quality Invoice Images for OCR

https://www.kaggle.com/datasets/osamahosamabdellatif/high-quality-invoice-images-for-ocr

The project uses the first 50 invoice images from Batch1_1.

The selected images were used as the clean reference set, and corresponding noisy/degraded versions were created as part of the project's OCR robustness evaluation.

Please refer to the original Kaggle dataset page for the current licensing and attribution requirements.
