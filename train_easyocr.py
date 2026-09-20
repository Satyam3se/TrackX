import os
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
import sys
import sys
import lmdb
import torch
import cv2
import numpy as np
import json
import pickle
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from tqdm import tqdm

# EasyOCR imports
import easyocr
from easyocr.utils import CTCLabelConverter

# Paths
LMDB_TRAIN_PATH = os.path.join('ocr_training_data', 'lmdb', 'train.lmdb')
LMDB_VAL_PATH = os.path.join('ocr_training_data', 'lmdb', 'val.lmdb')
OUTPUT_DIR = 'ocr_weights'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Hyperparameters
BATCH_SIZE = 4
EPOCHS = 2
LR = 1e-4
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Simple LMDB Dataset
class LMDBDataset(Dataset):
    def __init__(self, lmdb_path, transform=None):
        self.env = lmdb.open(lmdb_path, readonly=True, lock=False, readahead=False, max_readers=126)
        with self.env.begin(write=False) as txn:
            self.length = txn.stat()['entries']  # one entry per sample
        self.transform = transform

    def __len__(self):
        return self.length

    def __getitem__(self, idx):
        with self.env.begin(write=False) as txn:
            key = f"{idx:08d}".encode('ascii')
            entry_bytes = txn.get(key)
        if entry_bytes is None:
            raise KeyError(f"LMDB entry not found for index {idx}")
        entry = pickle.loads(entry_bytes)
        img_bytes = entry['image']
        label = entry['label']
        # Decode image (stored as PNG bytes)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Resize to fixed dimensions for batch consistency
        img = cv2.resize(img, (224, 224))
        if self.transform:
            img = self.transform(img)
        return img, label

# Transform to tensor and normalize like EasyOCR expects
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.5], std=[0.5])
])

train_dataset = LMDBDataset(LMDB_TRAIN_PATH, transform=transform)
val_dataset = LMDBDataset(LMDB_VAL_PATH, transform=transform)
train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0, pin_memory=True)
val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0, pin_memory=True)

# Load pretrained EasyOCR model (English + Hindi for Indian plates)
import time
import urllib.error

# Define where EasyOCR will store/download models
MODEL_DIR = os.path.join(os.getcwd(), 'easyocr_models')
os.makedirs(MODEL_DIR, exist_ok=True)

# Attempt to create the Reader with download disabled; if models are missing, we'll download manually with retries
# Initialize EasyOCR Reader (will download models automatically if not present)
reader = easyocr.Reader(['en', 'hi'], gpu=torch.cuda.is_available(), model_storage_directory=MODEL_DIR, download_enabled=True, verbose=False)

model = reader.recognizer
model = model.to(DEVICE)
model.train()

# EasyOCR uses CTC loss; get converter
charset = reader.character
converter = CTCLabelConverter(charset)
criterion = torch.nn.CTCLoss(blank=0, zero_infinity=True)
optimizer = torch.optim.AdamW(model.parameters(), lr=LR)

# Helper to perform a forward pass and recover from CUDA OOM by falling back to CPU
import traceback

def safe_forward(model, imgs, targets, device):
    try:
        preds = model(imgs, text=targets)
        return preds, device
    except RuntimeError as e:
        if 'out of memory' in str(e):
            # Log and switch to CPU
            print('⚠️ CUDA OOM detected – switching to CPU')
            torch.cuda.empty_cache()
            model_cpu = model.to('cpu')
            imgs_cpu = imgs.to('cpu')
            targets_cpu = targets.to('cpu')
            preds = model_cpu(imgs_cpu, text=targets_cpu)
            return preds, 'cpu'
        else:
            raise


def encode_labels(labels):
    # Clean and filter each label string
    cleaned = []
    for txt in labels:
        txt = txt.strip()
        txt = ''.join([c if c in charset else ' ' for c in txt])
        cleaned.append(txt)
    # Use EasyOCR converter to get encoded tensor and lengths tensor
    encoded, lengths = converter.encode(cleaned)
    return encoded, lengths

for epoch in range(1, EPOCHS + 1):
    model.train()
    running_loss = 0.0
    for imgs, labels in tqdm(train_loader, desc=f'Epoch {epoch}/{EPOCHS} - Training'):
        imgs = imgs.to(DEVICE)
        targets, target_lengths = encode_labels(labels)
        targets = targets.to(DEVICE)
        target_lengths = target_lengths.to(DEVICE)
        # Forward
        preds, used_device = safe_forward(model, imgs, targets, DEVICE)
        # preds shape: (batch, seq_len, num_classes)
        preds = preds.permute(1, 0, 2)  # (seq_len, batch, num_classes)
        input_lengths = torch.full(size=(preds.size(1),), fill_value=preds.size(0), dtype=torch.long).to(used_device)
        loss = criterion(preds, targets, input_lengths, target_lengths)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        running_loss += loss.item()
    avg_loss = running_loss / len(train_loader)
    print(f'\nEpoch {epoch} finished. Avg training loss: {avg_loss:.4f}')

    # Validation
    model.eval()
    val_loss = 0.0
    with torch.no_grad():
        for imgs, labels in tqdm(val_loader, desc='Validation'):
            imgs = imgs.to(DEVICE)
            targets, target_lengths = encode_labels(labels)
            targets = targets.to(DEVICE)
            target_lengths = target_lengths.to(DEVICE)
            preds, used_device = safe_forward(model, imgs, targets, DEVICE)
            preds = preds.permute(1, 0, 2)
            input_lengths = torch.full(size=(preds.size(1),), fill_value=preds.size(0), dtype=torch.long).to(used_device)
            loss = criterion(preds, targets, input_lengths, target_lengths)
            val_loss += loss.item()
    avg_val = val_loss / len(val_loader)
    print(f'Validation loss: {avg_val:.4f}')

# Save fine‑tuned weights
save_path = os.path.join(OUTPUT_DIR, 'indian_plates.pth')
torch.save(model.state_dict(), save_path)
print(f'\nTraining complete. Model saved to {save_path}')
