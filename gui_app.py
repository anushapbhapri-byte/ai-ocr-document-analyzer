import tkinter as tk
from validation_engine import validate_field
from openpyxl import Workbook
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
from data_extractor import extract_invoice_data
from confidence_engine import analyze_fields
import cv2
import os
import re

from ocr_engine import ocr_with_word_confidence
from preprocess import (
    to_gray,
    apply_threshold,
    adaptive_threshold,
    denoise,
    resize_image,
    sharpen_image
)
from analytics import generate_report

class OCRApp:
    def __init__(self, root):
        self.root = root
        self.root.state("zoomed")
        self.root.title("AI OCR Document Analyzer")
        self.root.configure(bg="#1e1e1e")

        # Modern progress bar style
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "AI.Horizontal.TProgressbar",
            troughcolor="#2d2d2d",
            background="#00ff99",
            bordercolor="#1e1e1e",
            lightcolor="#00ff99",
            darkcolor="#00ff99",
            thickness=12
        ) 

        tk.Label(
            root,
            text="OCR Document Analyzer",
            font=("Times New Roman", 22, "bold"),
            bg="#1e1e1e",
            fg="white"
        ).pack(pady=(0,0))

        tk.Button(root, text="Upload Image",
                  command=self.upload_image,
                  bg="#007acc", fg="white",
                  font=("Times New Roman", 12, "bold")).pack(pady=(0,0))

        # Status + Progress Row
        status_frame = tk.Frame(
            root,
            bg="#1e1e1e"
        )
        status_frame.pack(pady=0)

        self.status_label = tk.Label(
            status_frame,
            text="Ready",
            font=("Times New Roman", 12, "bold"),
            bg="#1e1e1e",
            fg="#00ff99"
        )

        self.status_label.pack(
            side="left",
            padx=10
        )

        self.progress = ttk.Progressbar(
            status_frame,
            orient="horizontal",
            length=380,
            mode="determinate",
            style="AI.Horizontal.TProgressbar"
        )

        self.progress.pack(
            side="left",
            padx=5
)

        self.best_frame = tk.Frame(
            root,
            bg="#1e1e1e"
        )
        self.best_frame.pack(pady=(0, 0))

        self.best_label = tk.Label(
            self.best_frame,
            text="",
            font=("Times New Roman", 14, "bold"),
            bg="#1e1e1e",
            fg="#00ff99"
        )
        self.best_label.pack(side="left")

        self.report_text = ""

        self.method_eye = tk.Button(
            self.best_frame,
            text="👁",
            font=("Segoe UI Emoji", 11),
            bg="#1e1e1e",
            fg="white",
            bd=0,
            cursor="hand2",
            activebackground="#1e1e1e",
            activeforeground="white",
            command=lambda: self.show_popup(    
                "Method Comparison",
                self.report_text
            )
        )
        self.method_eye.pack(side="left", padx=8)   

        self.main_frame = tk.Frame(root, bg="#1e1e1e")
        self.main_frame.pack(
            fill="both",
            expand=True,
            pady=(0,0)
        )

        # LEFT (IMAGE)
        self.left_frame = tk.Frame(self.main_frame, bg="#1e1e1e")
        self.left_frame.pack(side="left", fill="both", expand=True)

        self.canvas = tk.Canvas(self.left_frame, bg="#2d2d2d")
        self.canvas.pack(fill="both", expand=True)

        def draw_placeholder(event=None):
            if hasattr(self, "original_img"):
                return
        
            self.canvas.delete("placeholder")
            self.canvas.delete("image")

            w = self.canvas.winfo_width()
            h = self.canvas.winfo_height()

            cx = w // 2
            cy = h // 2

            # Document icon
            self.canvas.create_text(
                cx,
                cy - 60,
                text="📄",
                fill="#cfcfcf",
                font=("Segoe UI Emoji", 42),
                tags="placeholder"
            )

            # Placeholder text
            self.canvas.create_text(
                cx,
                cy + 40,
                text="No Invoice Loaded\n\nClick 'Upload Image'\nto start OCR analysis",
                fill="#cfcfcf",
                font=("Times New Roman", 16, "bold"),
                justify="center",
                tags="placeholder"
            )

        self.canvas.bind("<MouseWheel>", self.zoom)
        self.canvas.bind("<ButtonPress-1>", self.start_pan)
        self.canvas.bind("<B1-Motion>", self.pan_image)
        self.canvas.bind("<Configure>", draw_placeholder)
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0

        # ==========================
        # RIGHT PANEL
        # ==========================

        self.right_frame = tk.Frame(
            self.main_frame,
            bg="#1e1e1e",
            width=550
        )
        self.right_frame.pack(
            side="right",
            fill="both",
            padx=10,
            pady=(0,5)
        )

        # ==========================
        # METHOD COMPARISON
        # ==========================
        method_header = tk.Frame(
            self.right_frame,
            bg="#1e1e1e"
        )
        method_header.pack(fill="x", pady=(5,5))

        eye = tk.Label(
            method_header,
            text="👁",
            font=("Segoe UI Emoji",11),
            bg="#1e1e1e",
            fg="white",
            cursor="hand2"
        )
        
        # ==========================
        # EXTRACTED DATA
        # ==========================
        data_header = tk.Frame(
            self.right_frame,
            bg="#1e1e1e"
        )
        data_header.pack(fill="x", pady=(5,5))

        tk.Label(
            data_header,
            text="Extracted Data",
            font=("Times New Roman",14,"bold"),
            bg="#1e1e1e",
            fg="#00ff99"
        ).pack(side="left", padx=5)

        tk.Button(
            data_header,
            text="👁",
            font=("Segoe UI Emoji",11),
            bg="#1e1e1e",
            fg="white",
            bd=0,
            cursor="hand2",
            activebackground="#1e1e1e",
            activeforeground="white",
            command=lambda: self.show_popup(
                "Extracted Data",
                self.data_box.get("1.0", tk.END)
            )
        ).pack(side="right", padx=5)
        
        self.data_box = self.create_textbox(
            self.right_frame,
            6
        )

        # ==========================
        # BUTTONS
        # ==========================
    
        button_frame = tk.Frame(
            self.right_frame,
            bg="#1e1e1e"
        )
        button_frame.pack(
            pady=4
        )

        tk.Button(
            button_frame,
            text="💾 Save",
            command=self.save_text,
            bg="#4CAF50",
            fg="white",
            font=("Times New Roman",11,"bold"),
            width=14
        ).pack(side="left", padx=8)

        tk.Button(
            button_frame,
            text="⬇ Download",
            command=self.download_file,
            bg="#ff9800",
            fg="white",
            font=("Times New Roman",11,"bold"),
            width=14
        ).pack(side="left", padx=8)

    def create_textbox(self, parent, height):
        frame = tk.Frame(parent)
        frame.pack(fill="both", expand=True, pady=5)

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        text = tk.Text(frame, height=height,
                       bg="#2d2d2d", fg="white",
                       insertbackground="white",
                       yscrollcommand=scrollbar.set)

        text.pack(fill="both", expand=True)
        scrollbar.config(command=text.yview)

        return text

    def show_popup(self, title, content):

        popup = tk.Toplevel(self.root)
        popup.title(title)
        popup.state("zoomed")
        popup.configure(bg="#1e1e1e")

        heading = tk.Label(
            popup,
            text=title,
            font=("Times New Roman", 18, "bold"),
            bg="#1e1e1e",
            fg="#00ff99"
        )

        heading.pack(pady=10)

        frame = tk.Frame(
            popup,
            bg="#1e1e1e"
        )

        frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(
            side="right",
            fill="y"
        )

        text = tk.Text(
            frame,
            wrap="none",
            font=("Consolas", 13),
            bg="#2d2d2d",
            fg="white",
            insertbackground="white",
            padx=15,
            pady=15,
            yscrollcommand=scrollbar.set
        )

        text.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.config(
            command=text.yview
        )

        text.insert(
            "1.0",
            content
        )



    def show_validation_note(self, field, value, reason):
            """Show a small validation explanation window."""

            popup = tk.Toplevel(self.root)
            popup.title("Validation Issue")
            popup.configure(bg="#1e1e1e")
            popup.resizable(False, False)

            # Make it a small note-style window
            width = 380
            height = 190

            self.root.update_idletasks()

            x = self.root.winfo_x() + (
                self.root.winfo_width() - width
            ) // 2

            y = self.root.winfo_y() + (
                self.root.winfo_height() - height
            ) // 2

            popup.geometry(
                f"{width}x{height}+{x}+{y}"
            )

            popup.transient(self.root)
            popup.grab_set()

            tk.Label(
                popup,
                text="⚠ Validation Issue",
                font=("Times New Roman", 15, "bold"),
                bg="#1e1e1e",
                fg="#ffcc00"
            ).pack(pady=(12, 6))

            tk.Label(
                popup,
                text=f"Field: {field}",
                font=("Times New Roman", 11, "bold"),
                bg="#1e1e1e",
                fg="white"
            ).pack(anchor="w", padx=20)

            tk.Label(
                popup,
                text=f"Value: {value}",
                font=("Times New Roman", 11),
                bg="#1e1e1e",
                fg="#cccccc"
            ).pack(anchor="w", padx=20, pady=(2, 5))

            tk.Label(
                popup,
                text=f"Reason: {reason}",
                font=("Times New Roman", 11, "bold"),
                bg="#1e1e1e",
                fg="white",
                wraplength=340,
                justify="left"
            ).pack(anchor="w", padx=20, pady=(2, 8))

            tk.Button(
                popup,
                text="OK",
                command=popup.destroy,
                bg="#007acc",
                fg="white",
                font=("Times New Roman", 10, "bold"),
                width=8
            ).pack(pady=4)   

    def get_validation_reason(self, field, value, validation):
        """Return a user-friendly explanation for an invalid field."""

        # If validation_engine already provides a reason, use it.
        reason = validation.get("reason")

        if reason:
            return str(reason)

        field_lower = field.lower()
        value = str(value).strip()

        if field_lower == "vehicle number":
            return (
                "Invalid vehicle number format. "
                "Expected a valid vehicle registration number, "
                "for example KA01AB1234."
            )

        if field_lower == "total amount":
            return (
                "Numeric value expected. "
                "Enter the total amount as a number."
            )

        if field_lower == "ifsc":
            return (
                "Invalid IFSC format. "
                "Expected an 11-character IFSC code."
            )

        if field_lower == "gstin":
            return (
                "Invalid GSTIN format. "
                "Expected a valid 15-character GSTIN."
            )

        if field_lower == "invoice date":
            return (
                "Invalid invoice date format. "
                "Expected a date such as 22-Apr-25."
            )

        if field_lower == "invoice number":
            return (
                "Invalid invoice number format. "
                "Please check the invoice number."
            )

        if field_lower == "account number":
            return (
                "Invalid account number. "
                "A numeric account number is expected."
            )

        if field_lower == "bank":
            return (
                "Bank name could not be validated "
                "against the supported bank list."
            )

        return (
            f"The extracted value '{value}' does not "
            f"match the expected format for {field}."
        )


    def upload_image(self):
        path = filedialog.askopenfilename()

        if not path:
            return

        # Step 1
        self.status_label.config(text="Processing image...")
        self.progress["value"] = 20
        self.root.update()

        self.image = cv2.imread(path)

        methods = {
            "Original": self.image,
            "Gray": to_gray(self.image),
            "Threshold": apply_threshold(self.image),
            "Adaptive": adaptive_threshold(self.image),
            "Denoise": denoise(self.image),
            "Resize": resize_image(self.image),
            "Sharpen": sharpen_image(self.image)
        }

        self.status_label.config(text="Running OCR...")
        self.progress["value"] = 50
        self.root.update()

        results = {}

        for name, img in methods.items():

            start_time = __import__("time").perf_counter()

            try:
                text, word_data = ocr_with_word_confidence(img)

            except Exception as exc:
                print(f"OCR error in {name}: {exc}")
                text = ""
                word_data = []

            elapsed = (
                __import__("time").perf_counter()
                - start_time
            )

            # --------------------------------------------------------
            # Calculate actual average Tesseract confidence
            # --------------------------------------------------------

            valid_confidences = []

            for item in word_data:

                try:
                    conf = float(
                        item.get("confidence", -1)
                    )
                except (TypeError, ValueError):
                    conf = -1

                if conf >= 0:
                    valid_confidences.append(conf)

            if valid_confidences:

                average_confidence = (
                    sum(valid_confidences)
                    / len(valid_confidences)
                )

            else:
                average_confidence = 0.0

            results[name] = {
                "words": len(text.split()),
                "chars": len(text),
                "confidence": average_confidence,
                "time": elapsed,
                "text": text,
                "word_data": word_data
            }


        report, best_method = generate_report(
            results
        )

        self.report_text = report

        self.best_label.config(
            text=f"Best Method: {best_method}"
        )

        best_text = results[best_method]["text"]

        best_ocr_words = results[best_method]["word_data"]

        self.report_text = report

        self.best_label.config(text=f"Best Method: {best_method}")

        best_text = results[best_method]["text"]

        best_ocr_words = results[best_method]["word_data"]
        # Store actual Tesseract OCR confidence data
        # for later validation/re-scoring.
        self.ocr_words = best_ocr_words

        self.data_box.delete("1.0", tk.END)
        self.data_box.insert(tk.END, best_text)

        self.status_label.config(text="Extracting invoice data...")
        self.progress["value"] = 80
        self.root.update()

        invoice_data = extract_invoice_data(best_text)

        self.data_box.delete("1.0", tk.END)

        if invoice_data:

            # --------------------------------------------------------
            # FIELD CONFIDENCE
            # --------------------------------------------------------
            # confidence_engine.analyze_fields() expects the ACTUAL
            # Tesseract word-level OCR data so it can match each
            # extracted field to the OCR words that produced it.
            #
            # Do NOT pass one overall/average confidence here.
            # That would make field-level confidence meaningless.
            # --------------------------------------------------------

            confidence_results = analyze_fields(
                invoice_data,
                best_ocr_words
            )
            self.confidence_results = confidence_results
            # Validate extracted invoice fields
            validation_results = {}

            for field, value in invoice_data.items():
                validation_results[field] = validate_field(field, value)

            # Table header
            self.data_box.insert(
                tk.END,
                    f"{'FIELD':<22}"
                    f"{'EXTRACTED VALUE':<32}"
                    f"{'CONFIDENCE':<10}"
                    f"{'STATUS':<12}\n"
                )
            self.data_box.insert(
                tk.END,
                "-" * 76 + "\n"
            )

            manual_review_count = 0

            for key, result in confidence_results.items():

                value = str(result.get("value", ""))

                # Preserve unavailable confidence as None/N/A.
                # Do NOT convert None to 0% because 0% implies a
                # measured OCR confidence, which it is not.
                raw_confidence = result.get("confidence")

                if raw_confidence is None:
                    confidence = None
                else:
                    try:
                        confidence = max(
                            0,
                            min(round(float(raw_confidence)), 100)
                        )
                    except (TypeError, ValueError):
                        confidence = None
                # Keep long values from destroying the table layout
                if len(value) > 30:
                    value = value[:27] + "..."

                validation = validation_results.get(key, {})
                is_valid = validation.get("valid", True)

                if not is_valid:
                    review = "⚠ INVALID"
                    manual_review_count += 1

                    reason = self.get_validation_reason(
                        key,
                        value,
                        validation
                    )

                    self.data_box.insert(
                        tk.END,
                        f"{key:<22}"
                        f"{value:<32}"
                        f"{confidence:>3}%      "
                        f"{review:<12}"
                    )

                    info_button = tk.Button(
                        self.data_box,
                        text="?",
                        command=lambda f=key, v=value, r=reason:
                            self.show_validation_note(f, v, r),
                        bg="#ffcc00",
                        fg="black",
                        font=("Arial", 8, "bold"),
                        width=2,
                        height=1,
                        bd=0,
                        cursor="hand2"
                    )

                    self.data_box.window_create(
                        tk.END,
                        window=info_button
                    )

                    self.data_box.insert(
                        tk.END,
                        "\n"
                    )

                elif result["review"]:
                    review = "⚠ LOW OCR"
                    manual_review_count += 1

                    self.data_box.insert(
                        tk.END,
                        f"{key:<22}"
                        f"{value:<32}"
                        f"{('N/A' if confidence is None else str(confidence) + '%'):>6}      "
                        f"{review:<12}\n"
                    )

                else:
                    review = "✓ OK"

                    self.data_box.insert(
                        tk.END,
                        f"{key:<22}"
                        f"{value:<32}"
                        f"{('N/A' if confidence is None else str(confidence) + '%'):>6}      "
                        f"{review:<12}\n"
                    )

            self.data_box.insert(
                tk.END,
                "\n" + "=" * 76 + "\n"
            )

            if manual_review_count > 0:

                self.data_box.insert(
                    tk.END,
                    f"⚠ {manual_review_count} field(s) require manual verification.\n"
                )

            else:

                self.data_box.insert(
                    tk.END,
                    "✓ All extracted fields passed the confidence check.\n"
                )

        else:

            self.data_box.insert(
                tk.END,
                "No structured data found."
            )
        self.display_image(self.image)
    
        self.progress["value"] = 100
        self.status_label.config(text="Completed ✓")
        self.root.update()

    def extract_basic_data(self, text):
        data = ""
        if "Invoice" in text:
            data += "Invoice Detected\n"
        if "Total" in text:
            data += "Total Found\n"
        if "Bank" in text:
            data += "Bank Info Found\n"
        return data

    def display_image(self, img):
        self.original_img = img

        # Remove placeholder text
        self.canvas.delete("placeholder")

        self.update_image()

    def update_image(self):
        # Do nothing until an image has been uploaded
        if not hasattr(self, "original_img"):
            return

        img = cv2.cvtColor(self.original_img, cv2.COLOR_BGR2RGB)

        h, w = img.shape[:2]

        resized = cv2.resize(
            img,
            (int(w * self.scale), int(h * self.scale))
        )

        self.tk_img = ImageTk.PhotoImage(
            Image.fromarray(resized)
        )

        self.canvas.delete("image")

        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()

        x = max((canvas_w - self.tk_img.width()) // 2, 0)
        y = max((canvas_h - self.tk_img.height()) // 2, 0)

        self.canvas.create_image(
            x + self.offset_x,
            y + self.offset_y,
            anchor="nw",
            image=self.tk_img,
            tags="image"
        )

    def zoom(self, event):
        factor = 1.1 if event.delta > 0 else 0.9
        self.scale *= factor
        self.update_image()

    def start_pan(self, event):
        self.pan_start = (event.x, event.y)

    def pan_image(self, event):
        dx = event.x - self.pan_start[0]
        dy = event.y - self.pan_start[1]

        self.offset_x += dx
        self.offset_y += dy

        self.pan_start = (event.x, event.y)
        self.update_image()

    def save_text(self):
        """
        Re-validate and re-score edited invoice values.

        The displayed table is rebuilt from the edited values.
        Each field is validated exactly once.
        """

        text = self.data_box.get("1.0", tk.END).strip()

        updated_lines = []
        manual_review_count = 0

        # These are the fields produced by the invoice extractor.
        known_fields = [
            "Company Name",
            "GSTIN",
            "Invoice Number",
            "Invoice Date",
            "Vehicle Number",
            "Total Amount",
            "IFSC",
            "Bank",
            "Account Number",
        ]

        # Sort longest first so names containing another field name
        # are not matched incorrectly.
        known_fields.sort(key=len, reverse=True)

        field_pattern = "|".join(
            re.escape(field) for field in known_fields
        )

        # Read:
        # FIELD + edited VALUE + old CONFIDENCE + old STATUS
        row_pattern = re.compile(
            rf"^\s*(?P<field>{field_pattern})"
            rf"\s+(?P<value>.*?)"
            rf"\s+(?P<confidence>\d+(?:\.\d+)?)%"
            rf"\s+(?:✓ OK|⚠ INVALID|⚠ LOW OCR)\s*$"
        )

        for line in text.splitlines():

            stripped = line.strip()

            # Ignore headers, separators and summary messages.
            if (
                not stripped
                or stripped.startswith("FIELD")
                or set(stripped) == {"-"}
                or stripped.startswith("=")
                or "field(s) require manual verification" in stripped
                or "All extracted fields passed" in stripped
            ):
                continue

            match = row_pattern.match(line)

            # If this is not a valid data row, skip it.
            if not match:
                continue

            field = match.group("field").strip()
            value = match.group("value").strip()

            # Remove accidental trailing spaces.
            value = value.strip()

            if not field or not value:
                continue

            # ------------------------------------------------
            # 1. VALIDATE THE EDITED VALUE
            # ------------------------------------------------

            validation = validate_field(field, value)

            is_valid = bool(
                validation.get("valid", False)
            )

            # ------------------------------------------------
            # 2. CALCULATE CONFIDENCE FOR THE EDITED VALUE
            # ------------------------------------------------

            try:
                edited_result = analyze_fields(
                    {field: value},
                    getattr(self, "ocr_words", [])
                ).get(field, {})

                confidence = edited_result.get(
                    "confidence"
                )

            except (TypeError, ValueError):
                confidence = None

            if confidence is not None:
                confidence = max(
                    0,
                    min(
                        round(float(confidence)),
                        100
                    )
                )

            # ------------------------------------------------
            # 3. DETERMINE FINAL STATUS
            # ------------------------------------------------

            if not is_valid:

                status = "⚠ INVALID"
                manual_review_count += 1

                reason = self.get_validation_reason(
                    field,
                    value,
                    validation
                )

            elif edited_result.get("review", False):

                status = "⚠ LOW OCR"
                manual_review_count += 1
                reason = ""

            else:

                status = "✓ OK"
                reason = ""

            # ------------------------------------------------
            # 4. BUILD ONE CLEAN ROW
            # ------------------------------------------------

            updated_lines.append(
                {
                    "field": field,
                    "value": value,
                    "confidence": confidence,
                    "status": status,
                    "reason": reason
                }
            )

        # ----------------------------------------------------
        # REBUILD TABLE
        # ----------------------------------------------------

        final_text = (
            f"{'FIELD':<22}"
            f"{'EXTRACTED VALUE':<32}"
            f"{'CONF.':<10}"
            f"{'STATUS':<12}\n"
            + "-" * 76
            + "\n"
        )

        for row in updated_lines:

            final_text += (
                f"{row['field']:<22}"
                f"{row['value']:<32}"
                f"{row['confidence']:>3}%      "
                f"{row['status']:<12}"
            )

            # The ? button is added separately below.
            final_text += "\n"

        final_text += (
            "\n"
            + "=" * 76
            + "\n"
        )

        # ----------------------------------------------------
        # MANUAL REVIEW SUMMARY
        # ----------------------------------------------------

        if manual_review_count > 0:

            final_text += (
                f"⚠ {manual_review_count} "
                f"field(s) require manual verification.\n"
            )

        else:

            final_text += (
                "✓ All extracted fields passed "
                "the confidence check.\n"
            )

        # ----------------------------------------------------
        # UPDATE GUI
        # ----------------------------------------------------

        self.data_box.delete(
            "1.0",
            tk.END
        )

        self.data_box.insert(
            tk.END,
            final_text
        )

        # Add clickable validation buttons for invalid fields
        self.data_box.delete("1.0", tk.END)

        self.data_box.insert(
            tk.END,
            f"{'FIELD':<22}"
            f"{'EXTRACTED VALUE':<32}"
            f"{'CONF.':<10}"
            f"{'STATUS':<12}\n"
        )

        self.data_box.insert(
            tk.END,
            "-" * 76 + "\n"
        )

        for row in updated_lines:

            self.data_box.insert(
                tk.END,
                f"{row['field']:<22}"
                f"{row['value']:<32}"
                f"{row['confidence']:>3}%      "
                f"{row['status']:<12}"
            )

            if row["status"] == "⚠ INVALID":

                info_button = tk.Button(
                    self.data_box,
                    text="?",
                    command=lambda f=row["field"],
                                   v=row["value"],
                                   r=row["reason"]:
                        self.show_validation_note(f, v, r),
                    bg="#ffcc00",
                    fg="black",
                    font=("Arial", 8, "bold"),
                    width=2,
                    height=1,
                    bd=0,
                    cursor="hand2"
                )

                self.data_box.window_create(
                    tk.END,
                    window=info_button
                )

            self.data_box.insert(
                tk.END,
                "\n"
            )

        self.data_box.insert(
            tk.END,
            "\n" + "=" * 76 + "\n"
        )
      
        # ----------------------------------------------------
        # SAVE OUTPUT
        # ----------------------------------------------------

        os.makedirs(
            "outputs",
            exist_ok=True
        )

        with open(
            "outputs/final_output.txt",
            "w",
            encoding="utf-8"
        ) as f:

            f.write(final_text)

        self.best_label.config(
            text="Saved Successfully ✓"
        )

    def download_file(self):
        """
        Export the actual structured OCR results directly to Excel.

        The export does not parse the formatted GUI table. This keeps
        Excel columns aligned even when values, confidence text, or
        status text change length.
        """
        if not getattr(self, "confidence_results", None):
            messagebox.showwarning(
                "No Data",
                "Please process an invoice first."
            )
            return

        try:
            from openpyxl import Workbook
        except ImportError:
            messagebox.showerror(
                "Excel Export Error",
                "openpyxl is not installed. Run: pip install openpyxl"
            )
            return

        path = filedialog.asksaveasfilename(
            title="Save Excel Report",
            defaultextension=".xlsx",
            filetypes=[
                ("Excel Workbook", "*.xlsx"),
                ("All Files", "*.*"),
            ],
            initialfile="invoice_ocr_results.xlsx",
        )

        if not path:
            return

        try:
            wb = Workbook()
            ws = wb.active
            ws.title = "OCR Results"

            ws.append([
                "FIELD",
                "EXTRACTED VALUE",
                "CONFIDENCE",
                "STATUS",
                "MANUAL REVIEW",
            ])

            for field, result in self.confidence_results.items():
                value = result.get("value", "")
                confidence = result.get("confidence")
                status = result.get("status", "CHECK")
                review = result.get("review", True)

                ws.append([
                    field,
                    value,
                    "N/A" if confidence is None else f"{confidence}%",
                    status,
                    "YES" if review else "NO",
                ])

            ws.freeze_panes = "A2"
            ws.auto_filter.ref = f"A1:E{ws.max_row}"

            for column, width in {
                "A": 24,
                "B": 38,
                "C": 14,
                "D": 18,
                "E": 16,
            }.items():
                ws.column_dimensions[column].width = width

            wb.save(path)

            messagebox.showinfo(
                "Excel Export",
                f"Excel report saved successfully.\n\n{path}"
            )

        except Exception as exc:
            messagebox.showerror(
                "Excel Export Error",
                f"Could not create the Excel report:\n\n{exc}"
            )

if __name__ == "__main__":
    root = tk.Tk()
    app = OCRApp(root)
    root.mainloop()