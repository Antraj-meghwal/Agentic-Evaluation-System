#!/usr/bin/env python3
"""
Download a small DocLayNet sample set for GRADEOPS end-to-end testing.

Uses docling-project/DocLayNet-v1.2 (one parquet shard, first N rows only).
Outputs PNG/PDF files + manifest under examples/doclaynet_samples/.

Usage (from repo root, with venv active):
  pip install datasets pyarrow huggingface_hub
  python scripts/download_doclaynet_samples.py --count 5

Then in GRADEOPS UI:
  - Bulk upload PNGs/PDFs from examples/doclaynet_samples/
  - Attach examples/doclaynet_rubric.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "examples" / "doclaynet_samples"
DATASET_REPO = "docling-project/DocLayNet-v1.2"
# Smaller test shard (~266MB download, not the full 80k-page dataset)
PARQUET_FILE = "data/test-00004-of-00006.parquet"

DOC_LAYOUT_CLASSES = [
    "Caption",
    "Footnote",
    "Formula",
    "List-item",
    "Page-footer",
    "Page-header",
    "Picture",
    "Section-header",
    "Table",
    "Text",
    "Title",
]


def _pil_from_row_image(image):
    import io

    from PIL import Image

    if isinstance(image, Image.Image):
        return image.convert("RGB")
    if isinstance(image, dict):
        if image.get("bytes"):
            return Image.open(io.BytesIO(image["bytes"])).convert("RGB")
        if image.get("path"):
            return Image.open(image["path"]).convert("RGB")
    if isinstance(image, (bytes, bytearray)):
        return Image.open(io.BytesIO(image)).convert("RGB")
    return Image.open(image).convert("RGB")


def _save_row(row: dict, out_dir: Path, index: int) -> dict:
    meta = row.get("metadata") or {}
    category = meta.get("doc_category") or meta.get("category") or "unknown"
    doc_name = (meta.get("doc_name") or meta.get("document_id") or f"doc_{index}").replace("/", "_")
    page_no = meta.get("page_no", meta.get("page_number", index))

    base = f"{index:02d}_{category}_{doc_name}_p{page_no}"
    base = "".join(c if c.isalnum() or c in "._-" else "_" for c in base)[:120]

    image = row.get("image")
    if image is None:
        raise ValueError("Row has no image column")

    pil = _pil_from_row_image(image)
    png_path = out_dir / f"{base}.png"
    pil.save(png_path, format="PNG")

    pdf_path = None
    pdf_bytes = row.get("pdf")
    if pdf_bytes and isinstance(pdf_bytes, (bytes, bytearray)):
        pdf_path = out_dir / f"{base}.pdf"
        pdf_path.write_bytes(pdf_bytes)

    bboxes = row.get("bboxes") or []
    cat_ids = row.get("category_id") or []
    labels = []
    for cid in cat_ids[:20]:
        try:
            labels.append(DOC_LAYOUT_CLASSES[int(cid)])
        except (IndexError, TypeError, ValueError):
            labels.append(str(cid))

    return {
        "index": index,
        "category": category,
        "doc_name": doc_name,
        "page_no": page_no,
        "png": png_path.name,
        "pdf": pdf_path.name if pdf_path else None,
        "layout_labels_sample": labels[:10],
        "bbox_count": len(bboxes),
    }


def download_via_parquet(count: int, out_dir: Path) -> list[dict]:
    from huggingface_hub import hf_hub_download
    import pyarrow.parquet as pq

    print(f"Downloading shard {PARQUET_FILE} from {DATASET_REPO} …")
    print("(This is one split file ~250MB, not the full dataset.)")
    parquet_path = hf_hub_download(
        repo_id=DATASET_REPO,
        filename=PARQUET_FILE,
        repo_type="dataset",
    )

    pf = pq.ParquetFile(parquet_path)
    manifest: list[dict] = []
    seen = 0

    for batch in pf.iter_batches(batch_size=min(count, 8)):
        batch_dict = batch.to_pydict()
        n = len(next(iter(batch_dict.values())))
        for i in range(n):
            if seen >= count:
                return manifest
            row = {k: batch_dict[k][i] for k in batch_dict}
            try:
                entry = _save_row(row, out_dir, seen + 1)
                manifest.append(entry)
                print(f"  saved {entry['png']}" + (f" + {entry['pdf']}" if entry.get("pdf") else ""))
                seen += 1
            except Exception as exc:
                print(f"  skip row {seen}: {exc}", file=sys.stderr)
    return manifest


def download_via_streaming(count: int, out_dir: Path) -> list[dict]:
    from datasets import load_dataset

    print(f"Streaming {count} rows from {DATASET_REPO} (validation) …")
    ds = load_dataset(DATASET_REPO, split="validation", streaming=True)
    manifest: list[dict] = []
    for row in ds:
        if len(manifest) >= count:
            break
        try:
            entry = _save_row(row, out_dir, len(manifest) + 1)
            manifest.append(entry)
            print(f"  saved {entry['png']}")
        except Exception as exc:
            print(f"  skip: {exc}", file=sys.stderr)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Download DocLayNet samples for GRADEOPS")
    parser.add_argument("--count", type=int, default=5, help="Number of pages to export")
    parser.add_argument(
        "--method",
        choices=["parquet", "stream"],
        default="parquet",
        help="parquet=one test shard (recommended); stream=HF streaming (slower)",
    )
    parser.add_argument("--out", type=Path, default=OUT_DIR, help="Output directory")
    args = parser.parse_args()

    out_dir = args.out.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        if args.method == "parquet":
            manifest = download_via_parquet(args.count, out_dir)
        else:
            manifest = download_via_streaming(args.count, out_dir)
    except ImportError as exc:
        print(
            "Missing dependency. Run:\n"
            "  cd backend && source .venv/bin/activate\n"
            "  pip install pyarrow huggingface_hub datasets Pillow\n",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc

    if not manifest:
        print("No samples saved.", file=sys.stderr)
        return 1

    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print()
    print(f"Done — {len(manifest)} sample(s) in {out_dir}")
    print(f"Manifest: {manifest_path}")
    print()
    print("Test in GRADEOPS:")
    print("  1. Login as instructor@gradeops.edu / demo1234")
    print("  2. New Upload → select PNG/PDF files from examples/doclaynet_samples/")
    print("  3. Rubric: examples/doclaynet_rubric.json")
    print("  4. Extract → Run Tribunal (now)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
