# Carbon Crunch OCR – Short Documentation

## 1. Approach

The objective of this project was to build an OCR pipeline capable of processing semi-structured receipt/document images and converting the information into structured JSON data.

The pipeline follows these main stages:

**Input Images → Image Preprocessing → OCR → Field Extraction → Confidence Scoring → JSON Output → Expense Summary**

### Step 1: Image Preprocessing

Input receipt images are first processed to improve OCR quality. The preprocessing stage includes image enhancement and handling of image orientation/skew where required.

Multiple preprocessing approaches/variants can be used to improve the quality of the text supplied to the OCR engine.

### Step 2: OCR

The preprocessed image is passed through Tesseract OCR using `pytesseract`.

The OCR stage produces:

* Raw extracted text
* OCR confidence
* Preprocessing information
* Deskew information

The raw OCR text is retained in the output to make the extraction process easier to inspect and debug.

### Step 3: Structured Field Extraction

The OCR text is processed to identify the required receipt fields:

* Store name
* Date
* Items
* Total amount

Regular-expression and rule-based extraction techniques are used to identify relevant patterns from noisy OCR text.

For example, the total extraction logic can handle OCR text such as:

`TOTAL 5.11`

as well as text containing noise before the total:

`yy, TOTAL 5.11`

while avoiding incorrect matches such as `SUBTOTAL` and `TOTAL TAX`.

### Step 4: Confidence and Reliability

The system assigns confidence values to extracted fields.

Each field can be classified as:

* High confidence
* Medium confidence
* Low confidence

When important fields have low confidence, the system marks the receipt as requiring manual review.

This prevents uncertain OCR results from being treated as completely reliable data.

### Step 5: JSON Output

Each processed receipt generates an individual JSON file containing the extracted structured information, confidence values, reliability information, and relevant OCR/debug information.

The outputs are stored in:

`outputs/json/`

The pipeline generated **371 JSON outputs** for the provided dataset.

### Step 6: Expense Summary

The extracted transaction information is aggregated into an expense summary.

The summary contains:

* Total spend
* Number of transactions
* Spend grouped by store

The final summary is stored in:

`outputs/expense_summary.json`

---

## 2. Tools Used

### Programming Language

* Python

### OCR

* Tesseract OCR
* `pytesseract`

### Image Processing

* Pillow (PIL)

### Data Processing

* Pandas
* NumPy

### Testing

* Pytest

### Version Control

* Git
* GitHub

The implementation uses Python modules for preprocessing, OCR, extraction, confidence scoring, pipeline orchestration, and summary generation.

---

## 3. Challenges Faced

### Noisy OCR Output

Receipt images contain different fonts, layouts, image qualities, logos, and background elements. OCR therefore does not always return clean text.

For example, a receipt containing:

`TOTAL 5.11`

could produce OCR text such as:

`yy, TOTAL 5.11`

The extraction logic therefore needs to tolerate OCR noise instead of depending entirely on exact text formatting.

### Different Receipt Layouts

Receipts do not follow one universal format. Store names, dates, item descriptions, and totals can appear in different positions and formats.

A rule-based extraction approach therefore needs to rely on recognizable patterns rather than fixed coordinates alone.

### Store Name Variations

OCR can produce different versions of the same store name because of recognition errors. For example, small character-level differences may result in multiple representations of the same merchant.

This is an important limitation of basic OCR and can affect aggregation by store.

### Missing or Low-Confidence Fields

Some receipts may not contain clearly readable values for every required field. Instead of forcing an incorrect value, the pipeline allows fields to remain empty and marks the document for manual review when confidence is low.

### Total Extraction

The total amount is one of the most important fields in a receipt. OCR noise can place additional characters before the `TOTAL` keyword.

The extraction logic was improved to recognize totals even when OCR introduces preceding noise, while avoiding unrelated terms such as `SUBTOTAL`.

---

## 4. Improvements

Several improvements could make the system more accurate and production-ready.

### Better OCR Models

Tesseract is lightweight and works well for a basic OCR pipeline, but modern document AI/OCR models could improve recognition on difficult receipts.

Possible future approaches include transformer-based document OCR and cloud document intelligence services.

### Merchant Name Normalization

A normalization layer could group OCR variations of the same merchant into a canonical store name.

For example, different OCR outputs representing the same merchant could be mapped to one standardized merchant identifier.

### Better Item Extraction

Item-level extraction could be improved using layout-aware OCR and table/line-item detection. This would make it possible to reliably identify:

* Item description
* Quantity
* Unit price
* Line total

### Confidence Calibration

The current confidence system can be improved by calibrating confidence scores against a manually verified validation dataset.

This would allow confidence thresholds to be selected based on measured precision and recall rather than fixed rules.

### Human-in-the-Loop Review

A production system could provide a review interface where users can correct low-confidence fields.

Those corrections could then be stored as verified data for future model evaluation or improvement.

### Automated Evaluation Dataset

A manually labelled ground-truth dataset could be created to calculate field-level metrics such as:

* Store-name accuracy
* Date extraction accuracy
* Total extraction accuracy
* Item extraction precision/recall
* Overall document-level accuracy

This would provide a more objective measurement of system performance.

---

## Conclusion

The implemented system provides an end-to-end OCR pipeline that converts receipt images into structured JSON data, assigns confidence to extracted fields, identifies documents requiring manual review, and generates an aggregated expense summary.

The design focuses on robustness to noisy OCR output while keeping the implementation lightweight, explainable, and runnable locally.
