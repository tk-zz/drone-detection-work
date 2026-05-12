#!/usr/bin/env python3
"""Create a small YOLO-format VisDrone subset for lightweight local training."""

from __future__ import annotations

import argparse
import random
import shutil
from pathlib import Path


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def link_or_copy(src: Path, dst: Path, copy_files: bool) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() or dst.is_symlink():
        dst.unlink()
    if copy_files:
        shutil.copy2(src, dst)
    else:
        dst.symlink_to(src.resolve())


def sample_split(src_root: Path, dst_root: Path, split: str, count: int, seed: int, copy_files: bool) -> int:
    image_dir = src_root / "images" / split
    label_dir = src_root / "labels" / split
    images = sorted(p for p in image_dir.iterdir() if p.suffix.lower() in IMAGE_EXTS)

    rng = random.Random(seed)
    rng.shuffle(images)
    selected = images[: min(count, len(images))]

    for image_path in selected:
        label_path = label_dir / f"{image_path.stem}.txt"
        link_or_copy(image_path, dst_root / "images" / split / image_path.name, copy_files)
        if label_path.exists():
            link_or_copy(label_path, dst_root / "labels" / split / label_path.name, copy_files)
        else:
            empty_label = dst_root / "labels" / split / f"{image_path.stem}.txt"
            empty_label.parent.mkdir(parents=True, exist_ok=True)
            empty_label.write_text("", encoding="utf-8")

    return len(selected)


def write_yaml(dst_root: Path) -> None:
    yaml_text = f"""path: {dst_root.resolve()}
train: images/train
val: images/val

names:
  0: pedestrian
  1: people
  2: bicycle
  3: car
  4: van
  5: truck
  6: tricycle
  7: awning-tricycle
  8: bus
  9: motor
"""
    (dst_root / "visdrone_light.yaml").write_text(yaml_text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="datasets/VisDrone", help="Original VisDrone dataset root")
    parser.add_argument("--output", default="datasets/VisDroneLight", help="Subset output root")
    parser.add_argument("--train", type=int, default=800, help="Number of train images")
    parser.add_argument("--val", type=int, default=200, help="Number of validation images")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--copy", action="store_true", help="Copy files instead of symlinking")
    args = parser.parse_args()

    src_root = Path(args.source)
    dst_root = Path(args.output)
    if not src_root.exists():
        raise SystemExit(f"Source dataset not found: {src_root}")

    train_n = sample_split(src_root, dst_root, "train", args.train, args.seed, args.copy)
    val_n = sample_split(src_root, dst_root, "val", args.val, args.seed + 1, args.copy)
    write_yaml(dst_root)

    print(f"Created lightweight VisDrone subset at {dst_root}")
    print(f"train images: {train_n}")
    print(f"val images: {val_n}")
    print(f"yaml: {dst_root / 'visdrone_light.yaml'}")


if __name__ == "__main__":
    main()
