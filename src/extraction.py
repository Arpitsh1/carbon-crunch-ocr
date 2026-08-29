import re
from datetime import datetime


# ============================================================
# MONEY / DATE PATTERNS
# ============================================================

MONEY_RE = re.compile(
    r"(?<![\d.])"
    r"(?:RM\s*)?"
    r"([0-9]{1,6}(?:,[0-9]{3})*(?:\.[0-9]{1,2})?)"
    r"(?![\d.])",
    re.IGNORECASE,
)

DECIMAL_MONEY_RE = re.compile(
    r"(?<![\d.])"
    r"(?:RM\s*)?"
    r"([0-9]{1,6}(?:,[0-9]{3})*\.[0-9]{1,2})"
    r"(?![\d.])",
    re.IGNORECASE,
)

DATE_PATTERNS = [
    re.compile(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b"),
    re.compile(r"\b(\d{4}[/-]\d{1,2}[/-]\d{1,2})\b"),
]


# ============================================================
# TOTAL / PAYMENT KEYWORDS
# ============================================================

STRONG_TOTAL_RE = re.compile(
    r"\b("
    r"grand\s*total|"
    r"total\s*due|"
    r"amount\s*due|"
    r"net\s*total|"
    r"total\s*payable|"
    r"amount\s*payable|"
    r"balance\s*due|"
    r"total\s*incl|"
    r"total\s*including"
    r")\b",
    re.IGNORECASE,
)

NORMAL_TOTAL_RE = re.compile(
    r"\b(?:"
    r"total|"
    r"total\s*amount|"
    r"amount"
    r")\b",
    re.IGNORECASE,
)

BAD_TOTAL_RE = re.compile(
    r"\b("
    r"subtotal|"
    r"sub\s*total|"
    r"tax|"
    r"gst|"
    r"sst|"
    r"discount|"
    r"service\s*charge|"
    r"service\s*tax|"
    r"change|"
    r"cash|"
    r"payment|"
    r"paid|"
    r"balance|"
    r"item[s]?|"
    r"qty|"
    r"quantity"
    r")\b",
    re.IGNORECASE,
)


# ============================================================
# STORE / ADDRESS DETECTION
# ============================================================

ADDRESS_RE = re.compile(
    r"\b("
    r"jalan|"
    r"jln|"
    r"road|"
    r"rd\.?|"
    r"street|"
    r"st\.?|"
    r"avenue|"
    r"ave\.?|"
    r"lane|"
    r"lorong|"
    r"taman|"
    r"kampung|"
    r"kawasan|"
    r"industrial|"
    r"perindustrian|"
    r"selangor|"
    r"malaysia|"
    r"klang|"
    r"cheras|"
    r"subang|"
    r"damansara|"
    r"kepong|"
    r"maluri|"
    r"melawati|"
    r"banting|"
    r"shah\s*alam"
    r")\b",
    re.IGNORECASE,
)

DOCUMENT_RE = re.compile(
    r"\b("
    r"receipt|"
    r"invoice|"
    r"tax\s*invoice|"
    r"gst|"
    r"sst|"
    r"cashier|"
    r"operator|"
    r"terminal|"
    r"customer|"
    r"survey|"
    r"feedback|"
    r"thank\s*you|"
    r"welcome|"
    r"order\s*(no|number)|"
    r"invoice\s*(no|number)|"
    r"tel|"
    r"telephone|"
    r"phone|"
    r"fax"
    r")\b",
    re.IGNORECASE,
)

STORE_BAD_RE = re.compile(
    r"^\s*("
    r"item|"
    r"description|"
    r"details|"
    r"particulars|"
    r"quantity|"
    r"qty|"
    r"price|"
    r"amount|"
    r"total|"
    r"cash|"
    r"change|"
    r"payment"
    r")\s*$",
    re.IGNORECASE,
)


# ============================================================
# ITEM / NON-ITEM DETECTION
# ============================================================

ITEM_HEADER_RE = re.compile(
    r"\b("
    r"description|"
    r"item|"
    r"details|"
    r"particulars|"
    r"product"
    r")\b",
    re.IGNORECASE,
)

ITEM_PRICE_HEADER_RE = re.compile(
    r"\b("
    r"qty|"
    r"quantity|"
    r"price|"
    r"amount|"
    r"unit\s*price"
    r")\b",
    re.IGNORECASE,
)

NON_ITEM_RE = re.compile(
    r"\b("
    r"subtotal|"
    r"sub\s*total|"
    r"grand\s*total|"
    r"total\s*due|"
    r"amount\s*due|"
    r"tax|"
    r"gst|"
    r"sst|"
    r"discount|"
    r"service\s*charge|"
    r"service\s*tax|"
    r"rounding|"
    r"change|"
    r"cash|"
    r"payment|"
    r"visa|"
    r"mastercard|"
    r"credit|"
    r"debit|"
    r"balance|"
    r"amount\s*paid|"
    r"thank\s*you|"
    r"survey"
    r")\b",
    re.IGNORECASE,
)


# ============================================================
# HELPERS
# ============================================================

def norm_money(value):
    if value is None:
        return None

    try:
        value = (
            str(value)
            .replace("RM", "")
            .replace("rm", "")
            .replace(",", "")
            .strip()
        )

        number = float(value)

        if number < 0 or number > 1_000_000:
            return None

        return round(number, 2)

    except Exception:
        return None


def normalize_line(line):
    line = str(line)

    # Replace common OCR whitespace problems.
    line = re.sub(r"\s+", " ", line)

    return line.strip()


def alpha_count(text):
    return sum(ch.isalpha() for ch in text)


def digit_count(text):
    return sum(ch.isdigit() for ch in text)


def clean_store(text):
    text = re.sub(r"[^\w&.'\- ]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip(" -:._")


# ============================================================
# DATE EXTRACTION
# ============================================================

def parse_date(lines):

    for line in lines:

        for pattern in DATE_PATTERNS:

            for match in pattern.finditer(line):

                raw = match.group(1).replace("/", "-")

                formats = [
                    "%d-%m-%Y",
                    "%d-%m-%y",
                    "%Y-%m-%d",
                ]

                for fmt in formats:

                    try:
                        dt = datetime.strptime(raw, fmt)

                        # Receipt datasets can contain historical dates.
                        # Do not artificially reject valid dates because
                        # they are older than the current year.
                        if 1990 <= dt.year <= 2035:
                            return dt.strftime("%Y-%m-%d"), 0.96

                    except ValueError:
                        continue

    return None, 0.0


# ============================================================
# STORE NAME EXTRACTION
# ============================================================

def store_name(lines):

    candidates = []

    # Known retailer / business names.
    known_stores = [
        "walmart",
        "tesco",
        "target",
        "costco",
        "aldi",
        "lidl",
        "carrefour",
        "ikea",
        "mcdonald",
        "starbucks",
        "99 speed mart",
        "mr diy",
        "mr. diy",
        "aeon",
        "mydin",
        "popular book",
        "guardian",
        "harvey norman",
        "sushi mentai",
        "oldtown",
        "pappa",
        "pizza",
        "domino",
        "ikea",
        "super seven",
    ]

    for index, original in enumerate(lines[:18]):

        line = normalize_line(original)

        if not line:
            continue

        cleaned = clean_store(line)

        if len(cleaned) < 3:
            continue

        if len(cleaned) > 80:
            continue

        if STORE_BAD_RE.fullmatch(cleaned):
            continue

        # Reject addresses.
        if ADDRESS_RE.search(cleaned):
            continue

        # Reject document metadata.
        if DOCUMENT_RE.search(cleaned):
            continue

        alpha = alpha_count(cleaned)
        digits = digit_count(cleaned)

        if alpha < 3:
            continue

        # If the line is mostly numbers, it is almost certainly
        # an invoice number / address / ID.
        if digits > alpha:
            continue

        # Reject lines that contain a suspiciously large amount
        # of numeric content.
        if digits >= 8:
            continue

        # Store names are generally not extremely short OCR fragments.
        if alpha < 5 and len(cleaned) < 5:
            continue

        score = 0.30

        # Strong preference for lines near the top.
        if index == 0:
            score += 0.25
        elif index <= 2:
            score += 0.18
        elif index <= 5:
            score += 0.08

        # Known retailer.
        lower = cleaned.lower()

        for store in known_stores:
            if store in lower:
                score += 0.35
                break

        # Corporate suffix is useful evidence.
        if re.search(
            r"\b("
            r"sdn\.?\s*bhd\.?|"
            r"enterprise|"
            r"trading|"
            r"restaurant|"
            r"pharmacy|"
            r"hardware|"
            r"supermarket|"
            r"mart|"
            r"cafe|"
            r"bakery|"
            r"book|"
            r"furnishing"
            r")\b",
            cleaned,
            re.IGNORECASE,
        ):
            score += 0.12

        # Mostly uppercase often indicates printed business header.
        letters = [c for c in cleaned if c.isalpha()]

        if letters:
            uppercase_ratio = sum(c.isupper() for c in letters) / len(letters)

            if uppercase_ratio > 0.75:
                score += 0.08

        # Penalize suspicious OCR fragments.
        if len(cleaned.split()) == 1 and len(cleaned) <= 4:
            score -= 0.15

        if re.search(r"[^A-Za-z0-9&.'\- ]", cleaned):
            score -= 0.05

        candidates.append(
            (
                max(0.0, min(0.99, score)),
                cleaned,
            )
        )

    if not candidates:
        return None, 0.0

    candidates.sort(key=lambda x: x[0], reverse=True)

    score, store = candidates[0]

    return store, round(score, 3)


# ============================================================
# TOTAL EXTRACTION
# ============================================================

def extract_money_values(line):
    values = []

    for match in DECIMAL_MONEY_RE.finditer(line):

        value = norm_money(match.group(1))

        if value is not None:
            values.append(value)

    return values


def total_amount(lines):

    candidates = []

    for index, original in enumerate(lines):

        line = normalize_line(original)

        if not line:
            continue

        lower = line.lower()

        # Never interpret these as the final total.
        if re.search(
            r"\b("
            r"total\s*(tax|gst|sst|items?)|"
            r"tax\s*total|"
            r"gst\s*total|"
            r"items?\s*total"
            r")\b",
            lower,
        ):
            continue

        values = extract_money_values(line)

        if not values:
            continue

        # ----------------------------------------------------
        # STRONG TOTAL
        # ----------------------------------------------------

        if STRONG_TOTAL_RE.search(line):

            # Prefer the last decimal amount on the line.
            value = values[-1]

            score = 0.98

            # Total receipts above this are suspicious for this
            # dataset. Do not completely reject them, but penalize.
            if value > 10000:
                score -= 0.35

            if value > 100000:
                score -= 0.45

            candidates.append(
                (
                    score,
                    index,
                    value,
                    line,
                )
            )

            continue

        # ----------------------------------------------------
        # NORMAL "TOTAL"
        # ----------------------------------------------------

        if NORMAL_TOTAL_RE.search(line):

            # Do not accept a normal total if the line is actually
            # a tax/payment/change line.
            if BAD_TOTAL_RE.search(line):
                continue

            value = values[-1]

            score = 0.80

            if value > 10000:
                score -= 0.30

            if value > 100000:
                score -= 0.40

            candidates.append(
                (
                    score,
                    index,
                    value,
                    line,
                )
            )

    if not candidates:
        return None, 0.0, None

    # Prefer high score, then later total line.
    candidates.sort(
        key=lambda x: (x[0], x[1]),
        reverse=True,
    )

    score, index, value, line = candidates[0]

    # Extremely large values are almost certainly OCR mistakes
    # for ordinary receipts in this dataset.
    if value > 100000:
        return None, 0.0, None

    return round(value, 2), round(score, 3), line


# ============================================================
# ITEM EXTRACTION
# ============================================================

def find_item_start(lines):

    # First look for a normal table header.
    for i, line in enumerate(lines):

        if ITEM_HEADER_RE.search(line) and ITEM_PRICE_HEADER_RE.search(line):
            return i + 1

    # Fallback headers.
    for i, line in enumerate(lines):

        if re.fullmatch(
            r"\s*(item|description|details|particulars|product)\s*",
            line,
            re.IGNORECASE,
        ):
            return i + 1

    return None


def looks_like_product_line(line):

    if not line:
        return False

    if NON_ITEM_RE.search(line):
        return False

    # Must contain at least one decimal monetary value.
    money_matches = list(DECIMAL_MONEY_RE.finditer(line))

    if not money_matches:
        return False

    # Product lines normally have either:
    #   quantity + x + price
    #   multiple decimal amounts
    #   quantity + price
    quantity_hint = bool(
        re.search(
            r"\b\d+\s*[xX]\b",
            line,
        )
    )

    multiple_prices = len(money_matches) >= 2

    # Typical receipt:
    # 1 12.50
    leading_quantity = bool(
        re.match(
            r"^\s*\d+\s+",
            line,
        )
    )

    return quantity_hint or multiple_prices or leading_quantity


def extract_items(lines, total=None):

    start = find_item_start(lines)

    if start is None:
        return []

    stop = len(lines)

    for i in range(start, len(lines)):

        line = lines[i]

        # Once the final total/payment area starts,
        # stop looking for products.
        if STRONG_TOTAL_RE.search(line):
            stop = i
            break

        if re.search(
            r"\b("
            r"subtotal|"
            r"sub\s*total|"
            r"gst|"
            r"sst|"
            r"tax|"
            r"service\s*charge|"
            r"discount|"
            r"rounding|"
            r"change|"
            r"cash|"
            r"payment"
            r")\b",
            line,
            re.IGNORECASE,
        ):
            stop = i
            break

    items = []
    pending_description = []

    for line in lines[start:stop]:

        line = normalize_line(line)

        if not line:
            continue

        if not looks_like_product_line(line):

            # Keep short text as a possible description that belongs
            # to the following priced row.
            if (
                len(line) <= 100
                and alpha_count(line) >= 3
                and not NON_ITEM_RE.search(line)
            ):
                pending_description.append(line)

            continue

        matches = list(DECIMAL_MONEY_RE.finditer(line))

        if not matches:
            continue

        # Last monetary value is generally the line amount.
        price = norm_money(matches[-1].group(1))

        if price is None:
            continue

        if price < 0 or price > 100000:
            continue

        name = DECIMAL_MONEY_RE.sub("", line)

        # Remove quantity / x markers.
        name = re.sub(
            r"\b\d+\s*[xX]\b",
            " ",
            name,
        )

        name = re.sub(
            r"\bqty\s*[:=]?\s*\d+\b",
            " ",
            name,
            flags=re.IGNORECASE,
        )

        name = re.sub(
            r"^\s*\d+[.)\s]+",
            "",
            name,
        )

        name = re.sub(
            r"\s+",
            " ",
            name,
        ).strip(" -:.")

        if pending_description:
            name = " ".join(
                pending_description + [name]
            )
            pending_description = []

        if len(name) < 2:
            continue

        if len(name) > 120:
            continue

        if alpha_count(name) < 2:
            continue

        if NON_ITEM_RE.search(name):
            continue

        items.append(
            {
                "name": name,
                "price": round(price, 2),
                "confidence": 0.0,
            }
        )

    return items[:100]


# ============================================================
# CONFIDENCE
# ============================================================

def blended_confidence(ocr_confidence, extraction_confidence):

    value = (
        0.65 * ocr_confidence
        + 0.35 * extraction_confidence
    )

    return round(
        max(0.0, min(1.0, value)),
        3,
    )


def confidence_status(value):

    if value >= 0.85:
        return "high"

    if value >= 0.70:
        return "medium"

    return "low"


# ============================================================
# MAIN FIELD EXTRACTION
# ============================================================

def extract_fields(text, ocr_conf):

    lines = [
        normalize_line(line)
        for line in text.splitlines()
        if normalize_line(line)
    ]

    store, store_e = store_name(lines)

    date, date_e = parse_date(lines)

    total, total_e, total_line = total_amount(lines)

    items = extract_items(
        lines,
        total=total,
    )

    # --------------------------------------------------------
    # FIELD CONFIDENCE
    # --------------------------------------------------------

    store_conf = (
        blended_confidence(ocr_conf, store_e)
        if store
        else 0.0
    )

    date_conf = (
        blended_confidence(ocr_conf, date_e)
        if date
        else 0.0
    )

    total_conf = (
        blended_confidence(ocr_conf, total_e)
        if total is not None
        else 0.0
    )

    for item in items:

        # Item extraction is inherently less reliable than
        # a clearly detected total.
        item_conf = (
            0.60 * ocr_conf
            + 0.40 * 0.82
        )

        item["confidence"] = round(
            max(0.0, min(1.0, item_conf)),
            3,
        )

    result = {
        "store_name": {
            "value": store,
            "confidence": store_conf,
            "status": confidence_status(store_conf),
        },

        "date": {
            "value": date,
            "confidence": date_conf,
            "status": confidence_status(date_conf),
        },

        "items": items,

        "total_amount": {
            "value": total,
            "confidence": total_conf,
            "status": confidence_status(total_conf),
        },
    }

    # --------------------------------------------------------
    # MANUAL REVIEW
    # --------------------------------------------------------

    low_confidence_fields = []

    if store_conf < 0.70:
        low_confidence_fields.append("store_name")

    if date_conf < 0.70:
        low_confidence_fields.append("date")

    if total_conf < 0.70:
        low_confidence_fields.append("total_amount")

    if not items:
        low_confidence_fields.append("items")

    elif any(
        item["confidence"] < 0.70
        for item in items
    ):
        low_confidence_fields.append("items")

    # A receipt without a total should always be reviewed.
    if total is None:
        if "total_amount" not in low_confidence_fields:
            low_confidence_fields.append("total_amount")

    result["reliability"] = {
        "low_confidence_fields": low_confidence_fields,
        "requires_manual_review": bool(low_confidence_fields),
    }

    # Keep the detected total line for debugging.
    result["_debug"] = {
        "total_line": total_line,
        "line_count": len(lines),
        "ocr_confidence": round(ocr_conf, 3),
    }

    return result
