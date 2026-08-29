import argparse
import json
import os
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

from src.pipeline import process
from src.summary import build_summary


def process_one(path):
    return process(path)


def main():
    parser = argparse.ArgumentParser(
        description="Run receipt OCR pipeline in parallel."
    )

    parser.add_argument(
        "--input",
        default="data/input",
        help="Input receipt directory",
    )

    parser.add_argument(
        "--output",
        default="outputs/json",
        help="Output JSON directory",
    )

    parser.add_argument(
        "--summary",
        default="outputs/expense_summary.json",
        help="Expense summary output path",
    )

    parser.add_argument(
        "--workers",
        type=int,
        default=max(2, min(8, os.cpu_count() or 2)),
        help="Number of parallel workers",
    )

    args = parser.parse_args()

    input_dir = Path(args.input)
    output_dir = Path(args.output)

    output_dir.mkdir(parents=True, exist_ok=True)

    paths = sorted(
        [
            p
            for p in input_dir.rglob("*")
            if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
        ]
    )

    if not paths:
        print(f"No images found in {input_dir}")
        return

    records = []

    with ProcessPoolExecutor(max_workers=args.workers) as executor:

        futures = {
            executor.submit(process_one, path): path
            for path in paths
        }

        for index, future in enumerate(as_completed(futures), 1):

            path = futures[future]

            try:
                result = future.result()

                output_file = output_dir / f"{path.stem}.json"

                output_file.write_text(
                    json.dumps(
                        result,
                        indent=2,
                        ensure_ascii=False,
                    ),
                    encoding="utf-8",
                )

                records.append(result)

                total = result["total_amount"]["value"]
                confidence = result["total_amount"]["confidence"]

                print(
                    f"[{index}/{len(paths)}] "
                    f"{path.name}: "
                    f"total={total} "
                    f"conf={confidence:.2f}",
                    flush=True,
                )

            except Exception as error:

                print(
                    f"[ERROR] {path.name}: {error}",
                    flush=True,
                )

    summary = build_summary(records)

    Path(args.summary).write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    Path("outputs/all_results.json").write_text(
        json.dumps(records, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("\nSUMMARY")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()