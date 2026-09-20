# prepare_ocr_lmdb.py
"""Prepare LMDB training and validation datasets for EasyOCR fine‑tuning.

The script expects the following folder structure under the repository root:

```
ocr_training_data/
    images/   # plate image files (e.g., 00000000.jpg)
    labels/   # matching text files (e.g., 00000000.txt)
```

It creates LMDB databases at:
```
ocr_training_data/lmdb/train.lmdb
ocr_training_data/lmdb/val.lmdb
```

The LMDB entries store a simple ``{"image": <png bytes>, "label": "ABC1234"}`` dictionary
pickled with ``pickle.dumps``.
"""

import os
import random
import lmdb
import pickle
from pathlib import Path
from tqdm import tqdm
import cv2

# ---------- Configuration ----------
DATA_ROOT = Path(__file__).parent / "ocr_training_data"
IMAGES_DIR = DATA_ROOT / "images"
LABELS_DIR = DATA_ROOT / "labels"
LMDB_ROOT = DATA_ROOT / "lmdb"
TRAIN_RATIO = 0.9  # 90 % for training, 10 % for validation

def _load_label(label_path: Path) -> str:
    """Read the text label file and return a stripped string."""
    with open(label_path, "r", encoding="utf-8") as f:
        return f.read().strip()

def _encode_image(img_path: Path) -> bytes:
    """Read an image with OpenCV and encode it as PNG bytes.

    Using PNG keeps the data lossless and works well with the downstream
    ``cv2.imdecode`` call during training.
    """
    img = cv2.imread(str(img_path))
    if img is None:
        raise FileNotFoundError(f"Could not read image {img_path}")
    success, buf = cv2.imencode('.png', img)
    if not success:
        raise RuntimeError(f"Failed to encode {img_path} as PNG")
    return buf.tobytes()

def _write_lmdb(env_path: Path, entries: list):
    """Write a list of ``(image_bytes, label)`` tuples into an LMDB.

    The function stores each entry under a zero‑padded integer key (e.g., ``00000001``).
    """
    map_size = 1 << 40  # 1 TB – generous upper bound for safety
    env = lmdb.open(str(env_path), map_size=map_size)
    with env.begin(write=True) as txn:
        for idx, (img_bytes, label) in enumerate(tqdm(entries, desc=f"Writing {env_path.name}")):
            key = f"{idx:08d}".encode('ascii')
            value = pickle.dumps({"image": img_bytes, "label": label})
            txn.put(key, value)
    env.close()

def main():
    # Collect matching image/label pairs
    image_files = sorted(IMAGES_DIR.glob("*"))
    label_files = sorted(LABELS_DIR.glob("*"))
# Skip strict count check; mismatched pairs are handled later.
# if len(image_files) != len(label_files):
#     raise RuntimeError("Number of images and label files do not match.")

    pairs = []
    missing_labels = []
    for img_path in image_files:
        stem = img_path.stem
        label_path = LABELS_DIR / f"{stem}.txt"
        if not label_path.is_file():
            missing_labels.append(str(img_path.name))
            continue
        label = _load_label(label_path)
        img_bytes = _encode_image(img_path)
        pairs.append((img_bytes, label))
    if missing_labels:
        print(f"Skipped {len(missing_labels)} images without labels.")

    # Shuffle and split
    random.shuffle(pairs)
    split_idx = int(len(pairs) * TRAIN_RATIO)
    train_pairs = pairs[:split_idx]
    val_pairs = pairs[split_idx:]

    LMDB_ROOT.mkdir(parents=True, exist_ok=True)
    _write_lmdb(LMDB_ROOT / "train.lmdb", train_pairs)
    _write_lmdb(LMDB_ROOT / "val.lmdb", val_pairs)
    print(f"LMDB creation complete. Train: {len(train_pairs)} samples, Val: {len(val_pairs)} samples.")

if __name__ == "__main__":
    main()
