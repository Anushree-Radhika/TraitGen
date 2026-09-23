"""
Train PadChest X-ray report generation model on Modal GPU.

First-time setup (uploads dataset to cloud volume — only needed once):
    modal run main_modal.py --upload

Train:
    modal run main_modal.py
"""
import modal

app = modal.App("padchest-training")

image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install(
        "torch",
        "torchvision",
        "transformers",
        "tqdm",
        "pandas",
        "Pillow",
        "open_clip_torch",
        "peft",
        "timm",
        "scipy",
    )
    # Ship your Python source packages
    .add_local_python_source("dataset", "model")
    # Ship standalone .py modules
    .add_local_file("engine.py", remote_path="/root/engine.py")
    .add_local_file("utils.py", remote_path="/root/utils.py")
    .add_local_file("main.py", remote_path="/root/main.py")
)

# Persistent volume for the dataset (uploaded once, reused every run)
dataset_vol = modal.Volume.from_name("padchest-dataset", create_if_missing=True)

# Persistent volume for trained weights (survives across runs)
checkpoint_vol = modal.Volume.from_name("padchest-checkpoints", create_if_missing=True)


# ─── Training function (runs on cloud GPU) ──────────────────────────────────
@app.function(
    image=image,
    gpu="T4",
    timeout=6 * 60 * 60,  # 6 hours
    volumes={
        "/data": dataset_vol,
        "/root/output": checkpoint_vol,
    },
)
def train():
    import sys
    import os

    os.chdir("/root")
    sys.path.insert(0, "/root")

    # Verify dataset is available
    img_dir = "/data/PC/images-224/images-224"
    csv_path = "/data/PC/PADCHEST_chest_x_ray_images_labels_160K_01.02.19.csv"
    assert os.path.exists(csv_path), f"CSV not found! Run first: modal run main_modal.py --upload"
    img_count = len(os.listdir(img_dir))
    print(f"Dataset loaded: {img_count} images found")

    import main

    args = main.get_args_parser().parse_args([])
    args.data_root = "/data/PC"
    args.output_dir = "/root/output"
    args.epochs = 15
    args.batch_size = 32

    print("=" * 60)
    print("Starting PadChest training on Modal A100 GPU")
    print(f"  Epochs: {args.epochs}")
    print(f"  Batch size: {args.batch_size}")
    print(f"  Data root: {args.data_root}")
    print(f"  Output dir: {args.output_dir}")
    print("=" * 60)

    main.main(args)

    checkpoint_vol.commit()
    print("Checkpoint saved to Modal volume 'padchest-checkpoints'!")


# ─── Single local entrypoint ────────────────────────────────────────────────
@app.local_entrypoint()
def main_entrypoint(upload: bool = False):
    if upload:
        # ── Upload dataset to cloud volume ──
        from pathlib import Path

        print("Starting dataset upload to Modal volume...")

        # Upload CSV
        csv_local = "PC/PADCHEST_chest_x_ray_images_labels_160K_01.02.19.csv"
        print(f"Uploading CSV: {csv_local}")
        with open(csv_local, "rb") as f:
            dataset_vol.write_file(f"PC/{Path(csv_local).name}", f)

        # Upload images in batches
        img_dir = Path("PC/images-224/images-224")
        images = list(img_dir.iterdir())
        total = len(images)
        print(f"Uploading {total} images...")

        for i, img_path in enumerate(images):
            remote_path = f"PC/images-224/images-224/{img_path.name}"
            with open(img_path, "rb") as f:
                dataset_vol.write_file(remote_path, f)
            if (i + 1) % 5000 == 0 or (i + 1) == total:
                print(f"  Uploaded {i + 1}/{total} images")

        dataset_vol.commit()
        print("Dataset upload complete!")
    else:
        # ── Launch training ──
        print("Launching training on Modal A100 GPU...")
        train.remote()
        print("Training complete! Weights saved to Modal volume 'padchest-checkpoints'.")
