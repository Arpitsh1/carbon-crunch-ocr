# Carbon Crunch — Receipt OCR & Confidence-Aware Extraction

## 1. Objective
This project converts semi-structured receipt images into structured, confidence-aware JSON and generates an expense summary across receipts.

## 2. Pipeline
`Receipt image → resize/denoise/contrast → deskew → Tesseract OCR → text normalization → field extraction → confidence scoring → JSON → expense summary`

### Image preprocessing
- Resizes very large receipts to a practical OCR resolution.
- Converts RGB/BGR images to grayscale.
- Applies deskewing using foreground geometry.
- Uses non-local means denoising and CLAHE contrast enhancement.
- Generates adaptive-threshold output for difficult lighting/backgrounds.

### OCR
Tesseract OCR 5.x is used through `pytesseract`. Word-level confidence is obtained with `image_to_data`.

The pipeline currently uses PSM 6 as the primary receipt layout mode. The code is intentionally modular so PSM 4/11 or another OCR engine can be A/B tested without changing extraction logic.

## 3. Key Information Extraction
The extractor identifies:
- Store/vendor name from the upper receipt region.
- Transaction date using validated date patterns.
- Item rows only inside a detected item/description section and only when quantity/price evidence is present.
- Total amount using strong total keywords such as `Grand Total`, `Total Due`, `Total Payable`, and `Total`.

Conservative extraction is deliberate: a low-confidence missing value is safer for downstream financial processing than silently treating an address, phone number, tax amount, or invoice number as an item/total.

## 4. Confidence scoring
Each field receives a score from 0 to 1:

`field_confidence = 0.65 × OCR confidence + 0.35 × field evidence`

Field evidence includes:
- Date-format and calendar validation.
- Strong total keywords.
- Store-name position/layout heuristics.
- Item-row quantity/price structure.

Thresholds:
- **High:** ≥ 0.85
- **Medium:** 0.70–0.849
- **Low:** < 0.70

Any low-confidence field causes `requires_manual_review: true`.

## 5. Output example
```json
{
  "store_name": {
    "value": "Example Store",
    "confidence": 0.93,
    "status": "high"
  },
  "date": {
    "value": "2019-01-12",
    "confidence": 0.91,
    "status": "high"
  },
  "items": [
    {
      "name": "Milk",
      "price": 45.0,
      "confidence": 0.88
    }
  ],
  "total_amount": {
    "value": 45.0,
    "confidence": 0.95,
    "status": "high"
  },
  "reliability": {
    "low_confidence_fields": [],
    "requires_manual_review": false
  }
}
```

## 6. Expense summary
The summary calculates:
- Total spend across receipts with a usable total.
- Number of transactions with a usable total.
- Spend grouped by store.

## 7. Edge cases
The system is designed to fail safely on:
- Missing/partial receipts.
- Very noisy or blurred images.
- Skewed/rotated receipts.
- Different receipt widths and layouts.
- Missing dates or totals.
- Ambiguous OCR.

Missing or low-confidence fields are explicitly surfaced for manual review rather than fabricated.

## 8. Project structure
```text
carbon-crunch-ocr/
├── data/input/              # receipt images (not committed to Git)
├── outputs/json/            # per-receipt JSON
├── outputs/expense_summary.json
├── src/
│   ├── preprocessing.py
│   ├── ocr_engine.py
│   ├── extraction.py
│   ├── confidence.py
│   ├── pipeline.py
│   └── summary.py
├── run.py
├── requirements.txt
└── README.md
```

## 9. Run
Install Tesseract OCR separately and ensure `tesseract` is available on PATH.

```bash
pip install -r requirements.txt
python run.py --input data/input --output outputs/json
```

The command creates one JSON file per image plus:
- `outputs/all_results.json`
- `outputs/expense_summary.json`

## 10. Improvements / next steps
1. A/B test Tesseract PSM modes and preprocessing variants using a labeled validation set.
2. Add a receipt text-line detector to use bounding-box positions more explicitly.
3. Add a second OCR engine such as EasyOCR/PaddleOCR and use consensus for ambiguous fields.
4. Train/fine-tune a document information extraction model when enough labeled receipts are available.
5. Add exact-match / numeric tolerance metrics for store, date, item and total fields.
6. Add a human-review queue for low-confidence fields.

## 11. Important limitation
The supplied dataset contains heterogeneous receipt layouts and does not appear to include ground-truth structured labels. Therefore, true extraction accuracy should be reported only after manually labeling a validation subset. The repository includes the extraction pipeline and confidence mechanism but does not invent accuracy numbers.
