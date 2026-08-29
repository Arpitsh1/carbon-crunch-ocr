"""Small preprocessing A/B benchmark.

Compares:
1. Raw grayscale OCR
2. Enhanced OCR
3. Adaptive-threshold OCR

Uses Tesseract's mean word confidence and word count.
No ground-truth labels are assumed.

Note:
Tesseract confidence is NOT true OCR accuracy.
It is only a self-reported OCR confidence signal.
"""

import argparse
import random
import statistics
from pathlib import Path

from src.preprocessing import preprocess_image
from src.ocr_engine import run_ocr


def ocr_single(image):
    """Run OCR on a single image variant."""
    best, _ = run_ocr({"image": image})

    return {
        "confidence": best["ocr_confidence"],
        "words": len(best["df"]),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark OCR preprocessing variants."
    )

    parser.add_argument(
        "--input",
        default="data/input",
        help="Directory containing input images.",
    )

    parser.add_argument(
        "--sample",
        type=int,
        default=25,
        help="Number of random images to benchmark.",
    )

    args = parser.parse_args()

    # Supported image formats
    extensions = {".jpg", ".jpeg", ".png", ".webp"}

    paths = [
        path
        for path in Path(args.input).glob("*")
        if path.suffix.lower() in extensions
    ]

    if not paths:
        print(f"No images found in: {args.input}")
        return

    # Use a fixed seed so the benchmark is reproducible.
    random.seed(42)

    paths = random.sample(
        paths,
        min(args.sample, len(paths)),
    )

    print(f"Benchmarking {len(paths)} images...\n")

    raw_results = []
    enhanced_results = []
    adaptive_results = []

    for index, path in enumerate(paths, start=1):
        print(f"[{index}/{len(paths)}] {path.name}")

        # preprocess_image() expects a file path.
        #
        # It returns a dictionary containing:
        #   gray
        #   enhanced
        #   adaptive
        #   deskew_angle
        variants = preprocess_image(str(path))

        gray = variants["gray"]
        enhanced = variants["enhanced"]
        adaptive = variants["adaptive"]

        # Run OCR separately on each preprocessing variant.
        raw_result = ocr_single(gray)
        enhanced_result = ocr_single(enhanced)
        adaptive_result = ocr_single(adaptive)

        raw_results.append(
            (
                raw_result["confidence"],
                raw_result["words"],
            )
        )

        enhanced_results.append(
            (
                enhanced_result["confidence"],
                enhanced_result["words"],
            )
        )

        adaptive_results.append(
            (
                adaptive_result["confidence"],
                adaptive_result["words"],
            )
        )

    # Calculate mean OCR confidence.
    raw_conf = statistics.mean(
        result[0] for result in raw_results
    )

    enhanced_conf = statistics.mean(
        result[0] for result in enhanced_results
    )

    adaptive_conf = statistics.mean(
        result[0] for result in adaptive_results
    )

    # Calculate mean word count.
    raw_words = statistics.mean(
        result[1] for result in raw_results
    )

    enhanced_words = statistics.mean(
        result[1] for result in enhanced_results
    )

    adaptive_words = statistics.mean(
        result[1] for result in adaptive_results
    )

    # Print results.
    print("\n" + "=" * 55)
    print("OCR PREPROCESSING BENCHMARK")
    print("=" * 55)

    print(f"Sample size: {len(paths)}")

    print("\nMean OCR confidence:")
    print(f"  Raw grayscale : {raw_conf:.3f}")
    print(f"  Enhanced      : {enhanced_conf:.3f}")
    print(f"  Adaptive      : {adaptive_conf:.3f}")

    print("\nMean OCR words:")
    print(f"  Raw grayscale : {raw_words:.1f}")
    print(f"  Enhanced      : {enhanced_words:.1f}")
    print(f"  Adaptive      : {adaptive_words:.1f}")

    # Compare enhanced and adaptive against raw grayscale.
    print("\nRelative to raw grayscale:")

    print(
        f"  Enhanced confidence change: "
        f"{enhanced_conf - raw_conf:+.3f}"
    )

    print(
        f"  Adaptive confidence change: "
        f"{adaptive_conf - raw_conf:+.3f}"
    )

    print(
        f"  Enhanced word count change: "
        f"{enhanced_words - raw_words:+.1f}"
    )

    print(
        f"  Adaptive word count change: "
        f"{adaptive_words - raw_words:+.1f}"
    )

    # Determine which preprocessing method has the
    # highest average OCR confidence.
    mean_confidences = {
        "raw grayscale": raw_conf,
        "enhanced": enhanced_conf,
        "adaptive": adaptive_conf,
    }

    best_variant = max(
        mean_confidences,
        key=mean_confidences.get,
    )

    print("\nBest variant by mean confidence:")
    print(f"  {best_variant}")

    print("=" * 55)


if __name__ == "__main__":
    main()
