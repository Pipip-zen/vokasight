import os
import argparse
import yaml
from pathlib import Path
from ultralytics import YOLO

def download_roboflow_dataset(api_key: str, workspace: str = "fyp-fjnfe", project: str = "soldering-defect-good-condition", version: int = 1, download_dir: str = "dataset"):
    """
    Downloads dataset from Roboflow Universe using official Roboflow SDK.
    """
    from roboflow import Roboflow
    rf = Roboflow(api_key=api_key)
    proj = rf.workspace(workspace).project(project)
    dataset = proj.version(version).download("yolov8", location=download_dir)
    print(f"Dataset successfully downloaded to {download_dir}")
    return dataset.location

def train_model(data_yaml_path: str, epochs: int = 50, imgsz: int = 640, batch: int = 16, weights: str = "yolov8n.pt", project_name: str = "runs/vokasight_soldering"):
    """
    Trains YOLOv8 model for Soldering Defect Detection.
    """
    print(f"Loading base YOLOv8 model: {weights}")
    model = YOLO(weights)

    print(f"Starting training on {data_yaml_path} for {epochs} epochs...")
    results = model.train(
        data=data_yaml_path,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        name="soldering_defect_yolov8n",
        project=project_name,
        exist_ok=True
    )

    print("\nTraining completed successfully!")
    print(f"Best model weights saved at: {os.path.join(project_name, 'soldering_defect_yolov8n', 'weights', 'best.pt')}")
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VokaSight YOLOv8 Soldering Defect Training Script")
    parser.add_argument("--data", type=str, default="dataset/data.yaml", help="Path to data.yaml")
    parser.add_argument("--epochs", type=int, default=50, help="Number of training epochs")
    parser.add_argument("--batch", type=int, default=16, help="Batch size")
    parser.add_argument("--imgsz", type=int, default=640, help="Image size")
    parser.add_argument("--roboflow_key", type=str, default=None, help="Roboflow API Key if downloading")

    args = parser.parse_args()

    data_path = args.data
    if args.roboflow_key:
        data_path = download_roboflow_dataset(api_key=args.roboflow_key)
        data_path = os.path.join(data_path, "data.yaml")

    if not os.path.exists(data_path):
        print(f"Error: data.yaml not found at {data_path}. Please provide a valid path or Roboflow API key.")
    else:
        train_model(data_yaml_path=data_path, epochs=args.epochs, batch=args.batch, imgsz=args.imgsz)
