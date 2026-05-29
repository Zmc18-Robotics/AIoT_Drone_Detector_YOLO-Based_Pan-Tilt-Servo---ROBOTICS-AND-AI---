"""
=============================================================
  train_yolo.py  —  Training YOLOv8 untuk Deteksi Drone
=============================================================
  ALUR KERJA:
  1. Kumpulkan foto drone via main_yolo.py (tekan S/A)
  2. Simpan foto ke folder:
       Datasheet/Drone aman/Drone1/     <- foto drone aman tipe 1
       Datasheet/Drone aman/Drone2/     <- foto drone aman tipe 2
       Datasheet/Drone berbahaya/Drone1/ <- foto drone berbahaya tipe 1
       ...dst
  3. Jalankan label_manual.py untuk memberi bounding box
  4. Jalankan file ini:  python train_yolo.py
  5. Setelah selesai, jalankan main_yolo.py untuk deteksi real-time
=============================================================
"""

import os
import shutil
import random
import yaml
from pathlib import Path

# ─── Path konfigurasi ────────────────────────────────────────────────────────
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR    = os.path.dirname(BASE_DIR)   # folder "Anti Drone Turret Systems"
DATASHEET_DIR = os.path.join(PARENT_DIR, "Datasheet")
YOLO_DATA_DIR = os.path.join(BASE_DIR, "yolo_dataset")
MODEL_OUT_DIR = os.path.join(BASE_DIR, "drone_model")

TRAIN_RATIO = 0.80
EPOCHS      = 50
IMG_SIZE    = 320
BATCH_SIZE  = 8

# Model deteksi objek YOLOv8 nano (ringan, cocok untuk ESP32-CAM)
MODEL_BASE  = "yolov8n.pt"

IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

# Made by Zmc18-Robotics ~ @mc.zminecrafter_18 ~ Zmc18_Roboticz
def scan_classes(datasheet_dir):
    """
    Scan folder Datasheet -> Kategori -> Sub-kelas -> gambar berlabel (.txt)
    
    Contoh struktur:
      Datasheet/
        Drone aman/
          Drone1/   <- nama kelas = "Drone_aman_Drone1"
            img1.jpg
            img1.txt   <- bounding box dari label_manual.py
          Drone2/
            ...
        Drone berbahaya/
          Drone1/   <- nama kelas = "Drone_berbahaya_Drone1"
            ...
    """
    classes_dict = {}
    datasheet_path = Path(datasheet_dir)

    if not datasheet_path.exists():
        raise FileNotFoundError(f"Folder Datasheet tidak ditemukan: {datasheet_dir}")

    for kategori_dir in sorted(datasheet_path.iterdir()):
        if not kategori_dir.is_dir():
            continue
        for kelas_dir in sorted(kategori_dir.iterdir()):
            if not kelas_dir.is_dir():
                continue
            # Buat nama kelas gabungan: "Drone_aman_Drone1"
            kelas_name = f"{kategori_dir.name}_{kelas_dir.name}".replace(" ", "_")
            classes_dict[kelas_name] = str(kelas_dir)

    class_names = sorted(list(classes_dict.keys()))

    # Kumpulkan file gambar yang sudah punya label .txt
    valid_images = {name: [] for name in class_names}

    for class_name in class_names:
        class_dir = classes_dict[class_name]
        for img_name in os.listdir(class_dir):
            ext = os.path.splitext(img_name)[1].lower()
            if ext not in IMG_EXTS:
                continue
            img_path = os.path.join(class_dir, img_name)
            txt_path = os.path.splitext(img_path)[0] + ".txt"
            if os.path.exists(txt_path):
                valid_images[class_name].append((img_path, txt_path))

    return class_names, valid_images, classes_dict

# Made by Zmc18-Robotics ~ @mc.zminecrafter_18 ~ Zmc18_Roboticz
def build_dataset(class_names, valid_images, out_dir):
    """Buat struktur dataset YOLOv8 Object Detection."""
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)

    for split in ["train", "val"]:
        os.makedirs(os.path.join(out_dir, split, "images"), exist_ok=True)
        os.makedirs(os.path.join(out_dir, split, "labels"), exist_ok=True)

    total_train = 0
    total_val   = 0

    for class_name, img_txt_pairs in valid_images.items():
        if not img_txt_pairs:
            continue

        random.shuffle(img_txt_pairs)
        split_idx = max(1, int(len(img_txt_pairs) * TRAIN_RATIO))
        trn_pairs = img_txt_pairs[:split_idx]
        val_pairs = img_txt_pairs[split_idx:] or [img_txt_pairs[-1]]

        for img_path, txt_path in trn_pairs:
            shutil.copy2(img_path, os.path.join(out_dir, "train", "images"))
            shutil.copy2(txt_path, os.path.join(out_dir, "train", "labels"))
            total_train += 1

        for img_path, txt_path in val_pairs:
            shutil.copy2(img_path, os.path.join(out_dir, "val", "images"))
            shutil.copy2(txt_path, os.path.join(out_dir, "val", "labels"))
            total_val += 1

    print(f"\n[DATASET] Dataset dibuat di: {out_dir}")
    print(f"  Train : {total_train} gambar")
    print(f"  Val   : {total_val} gambar")

    # Buat data.yaml
    yaml_path = os.path.join(out_dir, "data.yaml")
    data_yaml = {
        "path":  out_dir,
        "train": "train/images",
        "val":   "val/images",
        "nc":    len(class_names),
        "names": class_names,
    }
    with open(yaml_path, "w") as f:
        yaml.dump(data_yaml, f, sort_keys=False, allow_unicode=True)

    return yaml_path


def print_class_summary(class_names, valid_images):
    print("\n[KELAS] Daftar kelas yang ditemukan:")
    for i, name in enumerate(class_names):
        count = len(valid_images[name])
        status = "✓" if count > 0 else "✗ (belum ada label)"
        print(f"  [{i:02d}] {name:<45} {count:>4} gambar  {status}")


def main():
    print("=" * 60)
    print("  TRAINING YOLOv8 — Anti Drone Turret System")
    print("=" * 60)

    try:
        from ultralytics import YOLO
    except ImportError:
        print("[ERROR] ultralytics belum terinstall!")
        print("        Jalankan: pip install ultralytics")
        return

    print(f"\n[SCAN] Membaca folder Datasheet:\n  {DATASHEET_DIR}\n")

    try:
        class_names, valid_images, classes_dict = scan_classes(DATASHEET_DIR)
    except FileNotFoundError as e:
        print(f"\n[ERROR] {e}")
        print("Pastikan folder Datasheet ada di:")
        print(f"  {DATASHEET_DIR}")
        return
# Made by Zmc18-Robotics ~ @mc.zminecrafter_18 ~ Zmc18_Roboticz
    total_labeled = sum(len(p) for p in valid_images.values())
    total_all     = 0
    for kelas_dir in classes_dict.values():
        for f in os.listdir(kelas_dir):
            if os.path.splitext(f)[1].lower() in IMG_EXTS:
                total_all += 1

    print_class_summary(class_names, valid_images)
    print(f"\n[INFO] Total foto      : {total_all}")
    print(f"[INFO] Foto berlabel   : {total_labeled}")
    print(f"[INFO] Foto belum label: {total_all - total_labeled}")

    if total_labeled == 0:
        print("\n[ERROR] TIDAK ADA GAMBAR BERLABEL (.txt)!")
        print("Silakan jalankan 'python label_manual.py' terlebih dahulu")
        print("untuk memberi bounding box pada gambar di folder Datasheet.")
        return

    if total_labeled < 10:
        print(f"\n[WARNING] Hanya {total_labeled} gambar berlabel.")
        print("  Disarankan minimal 50-100 gambar per kelas untuk hasil yang baik.")
        ans = input("  Lanjutkan training? (y/n): ").strip().lower()
        if ans != "y":
            print("Training dibatalkan.")
            return

    # Build dataset
    yaml_path = build_dataset(class_names, valid_images, YOLO_DATA_DIR)

    # Training
    print(f"\n[TRAIN] Memulai training Object Detection...")
    print(f"  Model   : {MODEL_BASE}")
    print(f"  Epochs  : {EPOCHS}")
    print(f"  ImgSize : {IMG_SIZE}")
    print(f"  Batch   : {BATCH_SIZE}")
    print(f"  Output  : {MODEL_OUT_DIR}\n")

    model = YOLO(MODEL_BASE)
    model.train(
        data     = yaml_path,
        epochs   = EPOCHS,
        imgsz    = IMG_SIZE,
        batch    = BATCH_SIZE,
        project  = BASE_DIR,
        name     = "drone_model",
        exist_ok = True,
        patience = 15,
        verbose  = True,
    )

    print("\n" + "=" * 60)
    print("  TRAINING SELESAI!")
    print("=" * 60)

    best_pt = os.path.join(MODEL_OUT_DIR, "weights", "best.pt")
    if os.path.exists(best_pt):
        print(f"  Model terbaik: {best_pt}")
        print("\n  Sekarang jalankan: python main_yolo.py")
    else:
        print(f"  Selesai. Cek folder: {MODEL_OUT_DIR}/weights/")
# Made by Zmc18-Robotics ~ @mc.zminecrafter_18 ~ Zmc18_Roboticz
    print("=" * 60)


if __name__ == "__main__":
    main()
