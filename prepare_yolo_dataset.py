import os
import glob
import random
import shutil
import xml.etree.ElementTree as ET

INPUT_IMG_DIR = r"c:\Users\harsh\.antigravity-ide\TrackX\input\number-plate-detection\images"
INPUT_ANN_DIR = r"c:\Users\harsh\.antigravity-ide\TrackX\input\number-plate-detection\annotations"
OUTPUT_DIR = r"c:\Users\harsh\.antigravity-ide\TrackX\yolo_dataset"

def convert_voc_to_yolo(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)
    
    yolo_lines = []
    for obj in root.findall('object'):
        bndbox = obj.find('bndbox')
        xmin = float(bndbox.find('xmin').text)
        xmax = float(bndbox.find('xmax').text)
        ymin = float(bndbox.find('ymin').text)
        ymax = float(bndbox.find('ymax').text)
        
        # YOLO format
        x_center = ((xmin + xmax) / 2) / w
        y_center = ((ymin + ymax) / 2) / h
        width = (xmax - xmin) / w
        height = (ymax - ymin) / h
        
        yolo_lines.append(f"0 {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")
        
    return yolo_lines

def main():
    os.makedirs(os.path.join(OUTPUT_DIR, "images", "train"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "images", "val"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "labels", "train"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "labels", "val"), exist_ok=True)
    
    # Get all xml files
    xml_files = glob.glob(os.path.join(INPUT_ANN_DIR, "*.xml"))
    random.shuffle(xml_files)
    
    split_idx = int(len(xml_files) * 0.8)
    train_files = xml_files[:split_idx]
    val_files = xml_files[split_idx:]
    
    def process_split(files, split_name):
        for xml_file in files:
            base_name = os.path.basename(xml_file).replace(".xml", "")
            img_file = os.path.join(INPUT_IMG_DIR, base_name + ".png")
            if not os.path.exists(img_file):
                img_file = os.path.join(INPUT_IMG_DIR, base_name + ".jpg")
            if not os.path.exists(img_file):
                continue
                
            # Copy image
            dest_img = os.path.join(OUTPUT_DIR, "images", split_name, os.path.basename(img_file))
            shutil.copy2(img_file, dest_img)
            
            # Write label
            yolo_lines = convert_voc_to_yolo(xml_file)
            dest_label = os.path.join(OUTPUT_DIR, "labels", split_name, base_name + ".txt")
            with open(dest_label, "w") as f:
                f.write("\n".join(yolo_lines) + "\n")
                
    print("Processing training set...")
    process_split(train_files, "train")
    print("Processing validation set...")
    process_split(val_files, "val")
    
    # Write data.yaml
    yaml_content = f"""train: {os.path.join(OUTPUT_DIR, 'images', 'train')}
val: {os.path.join(OUTPUT_DIR, 'images', 'val')}

nc: 1
names: ['license_plate']
"""
    yaml_path = os.path.join(OUTPUT_DIR, "data.yaml")
    with open(yaml_path, "w") as f:
        f.write(yaml_content)
        
    print(f"Dataset preparation complete! Data saved to {OUTPUT_DIR}")
    print(f"Created {yaml_path}")

if __name__ == "__main__":
    main()
