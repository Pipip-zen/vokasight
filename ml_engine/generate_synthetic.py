import os
import cv2
import numpy as np
import yaml

def generate_sample_dataset(output_dir="dataset", num_images=10):
    """
    Generates a sample synthetic dataset with bounding boxes for:
    0: good_soldering
    1: solder_bridge
    2: void
    """
    splits = ["train", "valid"]
    classes = ["good_soldering", "solder_bridge", "void"]

    for split in splits:
        img_dir = os.path.join(output_dir, split, "images")
        lbl_dir = os.path.join(output_dir, split, "labels")
        os.makedirs(img_dir, exist_ok=True)
        os.makedirs(lbl_dir, exist_ok=True)

        count = num_images if split == "train" else max(3, num_images // 3)
        for i in range(count):
            img_name = f"sample_{split}_{i:03d}.jpg"
            lbl_name = f"sample_{split}_{i:03d}.txt"

            img_path = os.path.join(img_dir, img_name)
            lbl_path = os.path.join(lbl_dir, lbl_name)

            # Generate synthetic PCB background
            img = np.zeros((640, 640, 3), dtype=np.uint8)
            img[:, :] = (30, 90, 40)  # PCB green

            # Draw PCB tracks
            cv2.line(img, (50, 100), (590, 100), (180, 180, 180), 4)
            cv2.line(img, (100, 50), (100, 590), (180, 180, 180), 4)

            # Draw solder pads and synthetic defects
            labels = []

            # 1. Good soldering joint
            cv2.circle(img, (200, 200), 25, (220, 220, 220), -1)
            # YOLO format: class x_center y_center width height (normalized)
            labels.append(f"0 0.3125 0.3125 0.08 0.08")

            # 2. Solder bridge
            cv2.rectangle(img, (350, 340), (450, 370), (200, 200, 200), -1)
            labels.append(f"1 0.625 0.5547 0.156 0.047")

            # 3. Void defect
            cv2.circle(img, (450, 200), 25, (220, 220, 220), -1)
            cv2.circle(img, (450, 200), 8, (40, 40, 40), -1)  # dark hole
            labels.append(f"2 0.703 0.3125 0.08 0.08")

            # Save image
            cv2.imwrite(img_path, img)

            # Save labels
            with open(lbl_path, "w") as f:
                f.write("\n".join(labels))

    # Save data.yaml
    data_yaml = {
        "path": os.path.abspath(output_dir),
        "train": "train/images",
        "val": "valid/images",
        "names": {i: name for i, name in enumerate(classes)}
    }

    yaml_path = os.path.join(output_dir, "data.yaml")
    with open(yaml_path, "w") as f:
        yaml.dump(data_yaml, f, default_flow_style=False)

    print(f"Sample synthetic dataset generated at {output_dir} with {len(classes)} classes!")
    return yaml_path

if __name__ == "__main__":
    generate_sample_dataset()
