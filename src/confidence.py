def confidence_explanation(result=None):
    return {
        'method': '0.65 * OCR confidence + 0.35 * field-specific evidence',
        'thresholds': {'high': 0.85, 'medium': 0.70, 'low': 0.0},
        'manual_review_rule': 'Any field below 0.70 triggers manual review.'
    }
