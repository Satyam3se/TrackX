import os
import subprocess
from pathlib import Path

# Load environment variables from .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

KAGGLE_USERNAME = os.getenv('KAGGLE_USERNAME')
KAGGLE_KEY = os.getenv('KAGGLE_KEY')

if not KAGGLE_USERNAME or not KAGGLE_KEY:
    raise RuntimeError('Kaggle credentials not found in environment variables. Please set KAGGLE_USERNAME and KAGGLE_KEY in .env')

# Ensure the kaggle CLI is configured
kaggle_config_path = Path.home() / '.kaggle'
kaggle_config_path.mkdir(parents=True, exist_ok=True)
(kaggle_config_path / 'kaggle.json').write_text(f"{{\"username\": \"{KAGGLE_USERNAME}\", \"key\": \"{KAGGLE_KEY}\"}}", encoding='utf-8')
os.chmod(kaggle_config_path / 'kaggle.json', 0o600)

def download_dataset(dataset_slug: str, path: str = "./kaggle_data"):
    """Download a Kaggle dataset using the Kaggle CLI.

    Args:
        dataset_slug (str): The dataset identifier in the form 'owner/dataset'.
        path (str): Destination directory for the dataset.
    """
    dest = Path(path)
    dest.mkdir(parents=True, exist_ok=True)
    cmd = ["kaggle", "datasets", "download", "-d", dataset_slug, "-p", str(dest), "--unzip"]
    try:
        subprocess.check_call(cmd)
        print(f"Dataset {dataset_slug} downloaded to {dest}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to download dataset {dataset_slug}: {e}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Download Kaggle dataset using stored credentials")
    parser.add_argument("dataset", help="Dataset slug (owner/dataset)")
    parser.add_argument("-o", "--output", default="./kaggle_data", help="Output directory")
    args = parser.parse_args()
    download_dataset(args.dataset, args.output)
