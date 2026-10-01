import os
import argparse
from roboflow import Roboflow
from ultralytics import YOLO

DATASETS_CONFIG = {
    "soldering_basic": {
        "workspace": "fyp-fjnfe",
        "project": "soldering-defect-good-condition",
        "version": 1,
        "weights_output": "ml_engine/weights/soldering_basic_best.pt"
    },
    "pcb_defect_general": {
        "workspace": "nbmachinevision",
        "project": "pcb-defect-vagef",
        "version": 1,
        "weights_output": "ml_engine/weights/pcb_defect_general_best.pt"
    },
    "nbcm_soldering": {
        "workspace": "sazeh",
        "project": "nbcm-soldering-defect",
        "version": 1,
        "weights_output": "ml_engine/weights/nbcm_soldering_best.pt"
    }
}

def train_local_module(api_key: str, module_key: str, epochs: int = 30, batch: int = 16):
    if module_key not in DATASETS_CONFIG:
        print(f"Unknown module key: {module_key}. Choose from: {list(DATASETS_CONFIG.keys())}")
        return

    cfg = DATASETS_CONFIG[module_key]
    download_dir = f"ml_engine/dataset/{module_key}"

    print(f"\n==========================================")
    print(f"Downloading {cfg['project']} from Roboflow...")
    print(f"==========================================")

    rf = Roboflow(api_key=api_key)
    project = rf.workspace(cfg["workspace"]).project(cfg["project"])
    dataset = project.version(cfg["version"]).download("yolov8", location=download_dir)
    data_yaml = os.path.join(dataset.location, "data.yaml")

    print(f"\nStarting local YOLOv8-Nano training for {epochs} epochs...")
    model = YOLO("yolov8n.pt")
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        batch=batch,
        imgsz=640,
        name=f"local_{module_key}",
        project="runs/detect/runs",
        exist_ok=True
    )

    trained_weights = f"runs/detect/runs/local_{module_key}/weights/best.pt"
    if os.path.exists(trained_weights):
        os.makedirs("ml_engine/weights", exist_ok=True)
        import shutil
        shutil.copy(trained_weights, cfg["weights_output"])
        shutil.copy(trained_weights, "ml_engine/weights/best.pt")
        print(f"\n✅ Local weights trained & saved to: {cfg['weights_output']}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train Local YOLOv8 Models for Roboflow Datasets")
    parser.add_argument("--roboflow_key", type=str, required=True, help="Roboflow API key to download dataset")
    parser.add_argument("--module", type=str, default="pcb_defect_general", choices=list(DATASETS_CONFIG.keys()) + ["all"])
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch", type=int, default=16)

    args = parser.parse_args()

    if args.module == "all":
        for k in DATASETS_CONFIG.keys():
            train_local_module(args.roboflow_key, k, epochs=args.epochs, batch=args.batch)
    else:
        train_local_module(args.roboflow_key, args.module, epochs=args.epochs, batch=args.batch)
