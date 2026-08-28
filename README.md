AI OCR Document Analyzer

An end-to-end intelligent invoice document-processing system that converts invoice images into structured data and evaluates the reliability of the extracted information.

The project goes beyond basic OCR by combining image preprocessing, OCR, field extraction, validation, confidence analysis, batch processing, benchmarking, and error analysis to support a practical automated-processing vs manual-review workflow.

🎯 Business Problem

Manual invoice data entry is repetitive, time-consuming, and vulnerable to transcription errors. OCR can automate extraction, but noisy or degraded documents can reduce extraction quality.

This project addresses that problem by building a pipeline that:

Accepts invoice images as input.

Applies image preprocessing to improve OCR readability.

Extracts text using OCR.

Converts unstructured OCR output into structured invoice fields.

Validates extracted values.

Evaluates confidence and data quality.

Supports batch processing.

Benchmarks multiple preprocessing approaches.

Categorizes extraction errors.

Provides analytics to understand when automated processing is reliable and when manual review may be required.

🔄 End-to-End Workflow

Invoice Image
      ↓
Image Preprocessing
      ↓
OCR Text Extraction
      ↓
Invoice Field Extraction
      ↓
Validation
      ↓
Confidence / Quality Assessment
      ↓
Auto-Accept or Manual Review
      ↓
Analytics + Benchmarking + Error Analysis

🧠 Key Features

OCR Processing

OCR-based invoice text extraction.

Support for noisy/degraded invoice images.

Multiple preprocessing approaches for comparison.

Image Preprocessing

The project evaluates preprocessing strategies such as:

Original

Grayscale

Thresholding

Denoising

Sharpening

Resizing

Adaptive preprocessing

Structured Invoice Extraction

Extracts relevant invoice information from OCR text into structured fields rather than leaving the result as raw text.

Validation

Extracted fields are checked using validation logic to identify potentially unreliable values.

Confidence Analysis

A confidence engine evaluates extraction quality and helps distinguish higher-confidence results from cases that may require additional review.

Batch Processing

Multiple invoices can be processed as a batch, allowing operational-level metrics to be calculated rather than evaluating only a single document.

Benchmarking

Different OCR/preprocessing methods can be compared using field-level extraction results and processing-quality metrics.

Error Analysis

Extraction errors are categorized to identify recurring failure patterns, including:

Missing extraction

Numeric / amount errors

Character / identifier errors

Analytics & Dashboard

The project includes analytics and dashboard components for presenting processing KPIs and benchmark results in a more business-oriented format.

Testing

A dedicated test suite is included under tests/ to verify project functionality.

📊 Benchmark & Error Analysis

The benchmark evaluates invoice field extraction across multiple OCR/preprocessing methods.

The benchmark pipeline produces outputs such as:

Field-level accuracy results

Method comparisons

Detailed field results

Manual-review comparisons

Error-category summaries

Field error summaries

Benchmark charts

Example benchmark outputs are stored under:

outputs/benchmark/

The error-analysis workflow generates:

outputs/benchmark/error_details.csv
outputs/benchmark/error_category_summary.csv
outputs/benchmark/field_error_summary.csv
outputs/benchmark/error_category_comparison.png

These outputs help move the project from simple OCR extraction toward measurable document-processing performance analysis.

📈 Business / Operational Perspective

The project is designed around a practical document-processing question:

Can an invoice be processed automatically with sufficient confidence, or should it be routed for manual review?

This creates a bridge between AI output and business operations.

Potential operational KPIs include:

KPI

Purpose

Invoices processed

Measures batch throughput

Auto-accepted invoices

Measures successful automated processing

Manual-review invoices

Measures documents requiring human intervention

Straight-through processing %

Measures automation effectiveness

Manual-review %

Measures review workload

Average processing time

Measures operational efficiency

Processing errors

Measures pipeline reliability

These metrics can be used to evaluate the potential operational value of an automated invoice-processing workflow.

📁 Dataset

The project uses invoice images from the Kaggle dataset:

High-Quality Invoice Images for OCR

Source:

https://www.kaggle.com/datasets/osamahosamabdellatif/high-quality-invoice-images-for-ocr

Dataset subset used

For this project, the first 50 invoice images from Batch1_1 were selected as the base dataset.

The selected clean invoice images were then processed to create noisy/degraded versions for OCR robustness evaluation.

Kaggle Dataset
      ↓
Batch1_1
      ↓
First 50 Invoice Images
      ↓
Custom Noise / Degradation
      ↓
Noisy Invoice Benchmark
      ↓
OCR Evaluation

The noisy images used in the benchmark are processed versions created as part of this project.

Dataset attribution: Please refer to the original Kaggle dataset page for the author's information and current licensing/usage terms.

🗂️ Project Structure

OCR_Project/
│
├── data/
│   ├── batch_invoices/
│   └── benchmark/
│       └── noisy_images/
│
├── outputs/
│   └── benchmark/
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
├── README.md
└── .gitignore

🛠️ Technology Stack

Python

Tesseract OCR

OpenCV

Pandas

NumPy

Matplotlib

Streamlit / dashboard components

Pytest

Git / GitHub

⚙️ Installation

1. Clone the repository

git clone https://github.com/anushabhapri-byte/ai-ocr-document-analyzer.git
cd ai-ocr-document-analyzer

2. Create a virtual environment

Windows:

python -m venv .venv
.venv\Scripts\activate

3. Install Python dependencies

pip install -r requirements.txt

4. Install Tesseract OCR

Tesseract OCR must be installed separately because it is an external OCR engine.

After installation, make sure the Tesseract executable is available to the project/environment.

▶️ Running the Project

The repository contains separate components for OCR processing, batch processing, analytics, benchmarking, error analysis, and the dashboard/GUI.

Run the appropriate entry point for the workflow you want to evaluate.

For example, the main pipeline can be started with:

python main.py

The dashboard component is available through:

dashboard.py

and the GUI application through:

gui_app.py

Refer to the source files and configured project workflow for the specific input/output paths used in your environment.

🧪 Running Tests

From the project root:

pytest

The test suite is located in:

tests/

📊 Generated Benchmark Outputs

The benchmark and error-analysis workflows can generate files such as:

outputs/benchmark/
├── benchmark_comparison.csv
├── detailed_field_results.csv
├── error_details.csv
├── error_category_summary.csv
├── field_error_summary.csv
├── field_comparison.csv
├── method_comparison.csv
├── all_methods_field_accuracy.png
├── all_methods_manual_review_rate.png
├── baseline_vs_best_metrics.png
├── error_category_comparison.png
├── field_accuracy_baseline_vs_best.png
├── field_level_accuracy_by_method.png
├── manual_review_rate_comparison.png
└── tesseract_confidence_comparison.png

The exact generated files may depend on which benchmark/analysis workflows have been executed.

🔍 Why This Project Is More Than Basic OCR

A basic OCR project generally follows:

Image → OCR → Text

This project extends that workflow into:

Image
  ↓
Preprocessing
  ↓
OCR
  ↓
Structured Extraction
  ↓
Validation
  ↓
Confidence Assessment
  ↓
Automation / Manual Review Decision
  ↓
Benchmarking
  ↓
Error Analysis
  ↓
Business Analytics

This makes the project relevant not only to AI / Computer Vision, but also to Data Analyst, Business Analyst, AI Analyst, and intelligent automation use cases.

🚀 Portfolio Value

This project demonstrates practical experience with:

Document AI

OCR

Computer vision preprocessing

Information extraction

Data validation

Confidence-based decision making

Batch processing

Benchmark design

Error analysis

KPI-oriented analytics

Automated document processing

The project focuses on measuring and improving the reliability of an AI-assisted business workflow rather than treating OCR accuracy as the only objective.

🔮 Future Improvements

Potential future enhancements include:

Improved extraction of complex invoice identifiers such as IBANs.

More robust handling of heavily degraded documents.

Larger and more diverse invoice benchmarks.

Additional OCR engines/models for comparison.

Improved confidence calibration.

Production-oriented API deployment.

Human-in-the-loop review workflows.

More advanced ROI and cost-saving analysis.

👤 Author

Anusha Bhapri

Computer Science & Engineering | MBA in Artificial Intelligence

📌 Dataset Attribution

This project uses a subset of the High-Quality Invoice Images for OCR dataset available through Kaggle.

Original dataset:

https://www.kaggle.com/datasets/osamahosamabdellatif/high-quality-invoice-images-for-ocr

The dataset is used as the source of the base invoice images. The noisy/degraded benchmark images were created as part of this project for OCR robustness evaluation.

Please consult the original dataset page for the latest licensing and attribution requirements.
