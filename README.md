<div align="center">

🔎 AI OCR Document Analyzer

Intelligent Invoice Processing • OCR Benchmarking • Document Quality Analysis

<p>
  <strong>An end-to-end OCR-based invoice processing system that converts invoice images into structured, validated data and identifies invoices that may require manual review.</strong>
</p>

<p>
  <img src="https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Tesseract-OCR-4285F4?style=for-the-badge" alt="Tesseract OCR">
  <img src="https://img.shields.io/badge/OpenCV-Image%20Processing-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white" alt="OpenCV">
  <img src="https://img.shields.io/badge/GUI-Tkinter-FFB000?style=for-the-badge" alt="Tkinter">
</p>

<p>
  <img src="https://img.shields.io/badge/Invoices-50%20Noisy%20Samples-6A1B9A?style=flat-square" alt="50 noisy invoices">
  <img src="https://img.shields.io/badge/Benchmark-7%20Preprocessing%20Methods-00897B?style=flat-square" alt="7 preprocessing methods">
  <img src="https://img.shields.io/badge/Status-Portfolio%20Project-2E7D32?style=flat-square" alt="Portfolio project">
</p>

</div>

🚀 What Is This Project?

This project goes beyond basic OCR.

It is a practical invoice-processing pipeline designed to answer two questions:

Can the system extract invoice information automatically?

and

How reliable is that extracted information?

The pipeline combines:

Image preprocessing → OCR → field extraction → normalization → validation → confidence analysis → benchmark evaluation → error analysis → automated/manual-review decision

The project was built around a controlled benchmark of 50 clean invoice images and 50 corresponding noisy invoice images, with manually verified ground truth used for evaluation.

🎯 Why I Built This

Manual invoice processing can involve repeatedly reading documents, entering values into systems, and checking whether extracted information is correct.

I wanted to build a system that could automate as much of this workflow as possible while still recognizing that not every OCR result should be trusted automatically.

The system is designed to:

Capability

Purpose

📄 Invoice extraction

Convert invoice images into structured fields

🖼️ Image preprocessing

Improve OCR readability under degraded conditions

🔤 OCR

Extract text using Tesseract

🧩 Field extraction

Convert OCR text into invoice attributes

✅ Validation

Check extracted values against expected rules

📊 Confidence analysis

Identify potentially uncertain OCR output

🧪 Benchmarking

Compare preprocessing strategies objectively

🔍 Error analysis

Understand why extraction fails

🤖 Review decision

Separate automatically acceptable invoices from review cases

📦 Batch processing

Process multiple invoices in one run

📑 Reporting

Export structured results and analytics

🏗️ System Architecture

                         ┌───────────────────────┐
                         │     Invoice Image     │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │ Image Preprocessing   │
                         │  • Gray               │
                         │  • Threshold          │
                         │  • Adaptive           │
                         │  • Denoise            │
                         │  • Resize             │
                         │  • Sharpen            │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │     Tesseract OCR     │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │ Structured Field      │
                         │ Extraction            │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │ Normalization         │
                         └───────────┬───────────┘
                                     │
                                     ▼
                    ┌────────────────────────────────┐
                    │ Validation + Confidence        │
                    │ Analysis                       │
                    └───────────────┬────────────────┘
                                    │
                         ┌──────────┴──────────┐
                         ▼                     ▼
                ┌─────────────────┐   ┌─────────────────┐
                │ Auto Accept     │   │ Manual Review   │
                └────────┬────────┘   └────────┬────────┘
                         │                     │
                         └──────────┬──────────┘
                                    ▼
                         ┌───────────────────────┐
                         │ Analytics / Export    │
                         │ CSV • Excel • Graphs  │
                         └───────────────────────┘

🧾 Invoice Fields Extracted

The current extraction pipeline works with these structured invoice fields:

#

Invoice Field

1

Invoice Number

2

Invoice Date

3

Seller Tax ID

4

Client Tax ID

5

Seller IBAN

6

Net Worth

7

VAT

8

Gross Worth

The extracted values are normalized and validated before the system makes a review decision.

🖼️ OCR Preprocessing Benchmark

Rather than assuming that one preprocessing technique is always best, I benchmarked multiple strategies.

Seven preprocessing methods

Method

Description

🧾 Original

OCR on the original image

⚫ Gray

Grayscale conversion

◼️ Threshold

Threshold-based binarization

🌓 Adaptive

Adaptive thresholding

🧹 Denoise

Noise reduction

🔍 Resize

Image scaling before OCR

✨ Sharpen

Sharpening to improve text edges

This makes the project an OCR evaluation system, rather than simply an OCR script.

🧪 Controlled Benchmark

The benchmark uses:

50 clean invoice images

50 corresponding noisy invoice images

Manually verified ground truth

Multiple preprocessing strategies

Field-level and character-level evaluation

Benchmark design

Original Dataset
      │
      ▼
Batch1_1
      │
      ▼
First 50 Invoice Images
      │
      ├─────────────────────┐
      │                     │
      ▼                     ▼
Clean Reference       Synthetic Noise /
Ground Truth          Degradation
      │                     │
      │                     ▼
      │               50 Noisy Invoices
      │                     │
      └──────────┬──────────┘
                 ▼
            OCR Pipeline
                 │
                 ▼
        Preprocessing Benchmark
                 │
                 ▼
       Accuracy + Error Analysis

Important evaluation principle

OCR predictions from noisy images are not used as ground truth.

The clean/reference data is used to establish the verified expected values, while noisy images are processed independently by the OCR pipeline.

📊 Benchmark Results

The current benchmark evaluated 50 noisy invoices.

<div align="center">

Metric

Original

Threshold

🎯 Field Accuracy

91.25%

94.75%

🔤 Character Accuracy

92.30%

95.06%

👥 Manual-Review Proxy

8.75%

5.25%

</div>

Key findings

Finding

Change

📈 Field accuracy

+3.50 percentage points

📈 Character accuracy

+2.76 percentage points

📉 Manual-review proxy

−3.50 percentage points

🏆 Best overall field accuracy

Threshold preprocessing

These results are specific to the controlled benchmark dataset and should not be interpreted as guaranteed performance on arbitrary real-world invoices.

📋 Field-Level Benchmark

The benchmark also evaluates individual invoice fields.

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

🔎 What this shows

Preprocessing does not improve every field equally.

In this benchmark, threshold preprocessing performed particularly well for monetary fields, while identifier fields such as IBAN remained more challenging.

That distinction is important because an overall OCR score can hide field-specific weaknesses.

🔍 Error Analysis

Accuracy tells us what happened.

Error analysis helps explain why it happened.

The project includes a dedicated error-analysis step that categorizes field-level mismatches into:

❌ Missing Extraction

🔢 Numeric / Amount Error

🔤 Character / Identifier Error

⚠️ Other Field Mismatch

Run error analysis

python error_analysis.py

Generated outputs

outputs/benchmark/error_details.csv
outputs/benchmark/error_category_summary.csv
outputs/benchmark/field_error_summary.csv
outputs/benchmark/error_category_comparison.png

This allows the pipeline to move from:

"OCR accuracy is X%"

to:

"These are the fields and error types responsible for the failures."

📦 Batch Invoice Processing

The project includes a batch-processing workflow for running the pipeline over multiple invoices.

Place invoices inside:

data/batch_invoices/

Then run:

python batch_processor.py

Batch KPIs

KPI

What it measures

📄 Total invoices

Documents processed

🤖 Auto accepted

Documents accepted automatically

👥 Manual review

Documents routed for review

❌ Processing errors

Documents that failed processing

⚡ Straight-through rate

Share processed without manual review

⏱️ Average processing time

Average time per invoice

Output files

outputs/batch/batch_invoice_results.csv
outputs/batch/batch_invoice_results.xlsx

📈 50-Invoice Batch Run

The current batch workflow was tested on 50 noisy invoices.

<div align="center">

Operational Metric

Result

📄 Total invoices

50

🤖 Auto accepted

37

👥 Manual review

13

❌ Processing errors

0

⚡ Straight-through rate

74.00%

👥 Manual-review rate

26.00%

⏱️ Average processing time

4.426 sec/invoice

</div>

Operational flow

50 Invoices
     │
     ▼
Batch Processing
     │
     ▼
OCR + Extraction + Validation
     │
     ├───────────────┐
     ▼               ▼
37 Auto Accepted   13 Manual Review
     │               │
     └───────┬───────┘
             ▼
        Final Results

The straight-through rate is specific to the current dataset and the project's review rules.

🎯 Confidence Is Not Accuracy

One of the important design decisions in this project is keeping OCR confidence separate from factual correctness.

Tesseract provides word-level confidence values. These can help identify potentially uncertain OCR output.

However:

OCR Confidence ≠ Factual Accuracy

A value can have a high OCR confidence score and still be wrong.

Therefore, the project evaluates OCR predictions independently against manually verified ground truth.

This distinction is particularly important for invoice automation because a confidently extracted wrong amount can be more damaging than an obviously low-confidence result.

✅ Validation Layer

The validation stage checks extracted values before the final review decision.

The workflow is:

OCR Text
   │
   ▼
Field Extraction
   │
   ▼
Normalization
   │
   ▼
Validation
   │
   ▼
Confidence / Quality Assessment
   │
   ▼
Accept OR Manual Review

The goal is not simply to extract something from every document.

The goal is to determine whether the extracted information is reliable enough for automated handling.

🖥️ Desktop Application

The repository also contains a Tkinter-based desktop application.

Run the GUI

python gui_app.py

GUI capabilities

📤 Upload invoice images

🖼️ View invoice images

🔤 Run OCR

🔄 Compare preprocessing approaches

📋 Display structured invoice fields

✅ Show validation status

📊 Display confidence information

💾 Save results

📑 Export results to Excel

📊 Analytics & Dashboard

The project includes analytics and dashboard components intended to answer practical business questions:

Operational questions

How many invoices were processed?

How many were automatically accepted?

How many required manual review?

Were there any processing failures?

How long does processing take?

Quality questions

Which preprocessing method performs best?

Which invoice fields are hardest to extract?

What types of OCR errors occur most frequently?

Does preprocessing improve extraction quality?

Where should human review be introduced?

This makes the project relevant not only as an OCR implementation, but also as a document-processing and decision-support workflow.

🗂️ Project Structure

ai-ocr-document-analyzer/
│
├── 📁 data/
│   ├── batch_invoices/
│   └── ...
│
├── 📁 outputs/
│   ├── benchmark/
│   ├── batch/
│   └── ...
│
├── 📁 tests/
│   └── test_project.py
│
├── 🐍 analytics.py
├── 🐍 batch_processor.py
├── 🐍 benchmark_evaluation.py
├── 🐍 confidence_engine.py
├── 🐍 create_ground_truth.py
├── 🐍 dashboard.py
├── 🐍 data_extractor.py
├── 🐍 error_analysis.py
├── 🐍 graph_engine.py
├── 🐍 gui_app.py
├── 🐍 main.py
├── 🐍 ocr_engine.py
├── 🐍 preprocess.py
├── 🐍 validation_engine.py
│
├── 📄 requirements.txt
├── 📄 .gitignore
└── 📄 README.md

🧰 Tech Stack

<div align="center">

Technology

Role

🐍 Python

Core implementation

🔤 Tesseract OCR

Text recognition

👁️ OpenCV

Image preprocessing

🖥️ Tkinter

Desktop GUI

📊 Pandas

Data processing and analysis

📈 Matplotlib

Benchmark and analytics visualizations

📑 Excel / CSV

Result export

🧪 Pytest

Testing

</div>

⚙️ Installation & Setup

1. Clone the repository

git clone https://github.com/anushabhapri-byte/ai-ocr-document-analyzer.git
cd ai-ocr-document-analyzer

2. Create a virtual environment

python -m venv .venv

3. Activate the environment

Windows PowerShell

.\.venv\Scripts\Activate.ps1

4. Install Python dependencies

python -m pip install -r requirements.txt

5. Install Tesseract OCR

Tesseract is an external dependency and must be installed separately.

After installation, verify that Tesseract is available to the project.

▶️ Running the Project

Main pipeline

python main.py

Desktop GUI

python gui_app.py

Batch processing

python batch_processor.py

Benchmark evaluation

python benchmark_evaluation.py

Error analysis

python error_analysis.py

Tests

python -m pytest

🧪 Testing

The repository includes automated tests under:

tests/test_project.py

Run:

python -m pytest

The test suite helps verify that the project's processing components continue to behave as expected as the pipeline evolves.

🗃️ Dataset & Data Generation

The project uses synthetic/demo invoice images from the Kaggle dataset:

High Quality Invoice Images for OCR

https://www.kaggle.com/datasets/osamahosamabdellatif/high-quality-invoice-images-for-ocr

Dataset selection

For this project:

Source: Batch1_1

Selected: First 50 invoice images

Clean images: Used to establish verified reference data

Noisy images: Generated by applying synthetic noise/degradation as part of this project

Data flow

Kaggle Dataset
      │
      ▼
   Batch1_1
      │
      ▼
First 50 Images
      │
      ├─────────────────┐
      │                 │
      ▼                 ▼
Clean Images       Synthetic Noise
      │                 │
      ▼                 ▼
Ground Truth      Noisy Invoices
      │                 │
      └────────┬────────┘
               ▼
          OCR Evaluation

Dataset attribution: The original invoice images come from the Kaggle dataset linked above. Synthetic noise/degradation was introduced for this project's evaluation. Please refer to the original dataset page for the applicable license and attribution requirements.

📌 Important Limitations

This project is a controlled OCR benchmark and portfolio implementation, not a production invoice-processing platform.

Current limitations

The benchmark contains 50 selected invoice images.

The invoices are synthetic/demo documents from the referenced Kaggle dataset.

Noise/degradation is synthetically introduced.

Benchmark results may not generalize to arbitrary real-world invoices.

Tesseract-based OCR can struggle with complex layouts, unusual fonts, severe degradation, and ambiguous characters.

The manual-review rate depends on the project's current validation/review rules.

Processing time depends on the local machine and environment.

These limitations are intentionally documented because benchmark transparency is as important as reporting a high accuracy number.

💡 What Makes This More Than an OCR Script?

A simple OCR project might look like:

Image → OCR → Text

This project expands that into:

Image
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
Benchmarking
  ↓
Error Analysis
  ↓
Automated Decision
  ↓
Human Review When Needed
  ↓
Analytics + Export

The focus is therefore on reliability, evaluation, and operational decision-making, not just text extraction.

📈 Project Highlights

<div align="center">

🔢 50

Noisy invoices benchmarked

🧪 7

Preprocessing strategies evaluated

🎯 94.75%

Best field accuracy in current benchmark

⚡ 74%

Straight-through rate in current 50-invoice batch

❌ 0

Processing errors in current batch run

</div>

🧠 Key Learning

The most important takeaway from this project was:

Better OCR does not simply mean extracting more text. It means knowing when the extracted information can be trusted.

That led to the addition of:

benchmarking → ground truth → validation → confidence analysis → error analysis → manual-review routing

This makes the system more aligned with how document-processing automation would need to operate in a real business environment.

🔮 Future Improvements

Potential next steps include:

📐 Layout-aware document understanding

🤖 Transformer-based OCR/document models

🧾 More diverse invoice templates

🌍 Multi-language invoice support

🧠 Improved field-level confidence scoring

🔁 Human-in-the-loop feedback

🌐 Web-based deployment

🐳 Dockerized deployment

☁️ Cloud-based document processing

📊 Larger benchmark datasets

🔬 More robust noise and degradation simulation

⚙️ Production-grade logging and monitoring

👩‍💻 Project Author

<div align="center">

Anusha Bhapri

Computer Science & Engineering + MBA in Artificial Intelligence

AI • Data Analytics • Business Analysis • Intelligent Document Processing

</div>

⭐ If You Found This Useful

If this project is useful or interesting, consider giving the repository a star and exploring the implementation.

<div align="center">

AI OCR Document Analyzer

From invoice image → structured data → quality evaluation → business decision

</div>
