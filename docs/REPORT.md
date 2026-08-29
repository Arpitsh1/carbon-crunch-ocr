# Carbon Crunch — Short Technical Report

## Approach
The system treats receipt understanding as a modular pipeline. First, OpenCV normalizes image scale and converts receipts to a cleaner grayscale/contrast-enhanced representation. A geometry-based deskew step addresses rotation, while denoising and adaptive thresholding are available for difficult images. Tesseract OCR then returns recognized text and word-level confidence scores.

The extraction layer converts OCR text into structured fields. Vendor detection focuses on the upper portion of the receipt and rejects common metadata/taglines. Dates are accepted only after calendar validation. Total extraction prioritizes strong labels such as Grand Total, Total Due, and Total Payable. Item extraction is intentionally conservative: rows must occur after an item/description header and contain quantity/price evidence, reducing false positives from phone numbers, addresses, invoice numbers, tax and payment lines.

## Confidence and reliability
Confidence is not copied blindly from a single OCR token. The system combines OCR confidence with field-specific evidence. A date receives stronger evidence when it matches a valid date and falls within a plausible range; totals receive stronger evidence when found next to a strong total keyword; item rows receive evidence from receipt-table structure.

The final field score is:

`0.65 × OCR confidence + 0.35 × field evidence`

Scores below 0.70 are marked low-confidence and trigger `requires_manual_review=true`.

## Dataset observations
The supplied receipts are heterogeneous: narrow thermal receipts, larger invoice-style documents, photographic captures, skewed receipts, varied typography, and different vendor layouts. Some images contain large white margins or background context. This makes a single fixed coordinate template unsuitable and motivates OCR plus heuristics rather than hard-coded receipt coordinates.

## Challenges
1. OCR can confuse digits and letters, especially on faint thermal print.
2. Receipt dates appear in several formats.
3. Addresses, telephone numbers, invoice IDs and product codes contain numbers that can be mistaken for prices.
4. `Total`, `Subtotal`, tax, rounding and payment amounts may all occur together.
5. Some receipts are partially visible or visually degraded.

## Improvements
A production version should add a second OCR engine and use consensus for ambiguous fields, learn line/region structure from bounding boxes, and maintain a labeled validation set for objective field-level precision/recall. A lightweight document model could replace heuristics after sufficient labels are collected.

## Evaluation
No ground-truth structured labels were supplied with the image collection, so this submission deliberately does not fabricate an accuracy percentage. For formal evaluation, manually label a stratified validation subset and report:
- Store-name exact/normalized match accuracy
- Date exact match accuracy
- Total amount accuracy within a small numeric tolerance
- Item precision/recall and price accuracy
- Percentage of fields correctly flagged for manual review
- OCR confidence calibration

This makes the reported score reproducible and defensible.
