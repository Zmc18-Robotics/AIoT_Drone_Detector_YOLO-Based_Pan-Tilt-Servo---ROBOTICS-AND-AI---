"""
=============================================================
  label_manual.py  —  Labeling Bounding Box untuk Dataset Drone
=============================================================
  Cara pakai:
  1. Pastikan foto drone sudah ada di folder Datasheet/
       Datasheet/Drone aman/Drone1/
       Datasheet/Drone aman/Drone2/
       Datasheet/Drone berbahaya/Drone1/
       ...dst
  2. Jalankan:  python label_manual.py
  3. Pilih folder yang ingin dilabel dari menu
  4. Untuk setiap gambar:
       - Klik + drag untuk membuat kotak (bounding box) di atas drone
       - Tekan ENTER / SPASI : simpan & lanjut ke gambar berikutnya
       - Tekan C             : hapus kotak terakhir (undo)
       - Tekan R             : reset semua kotak di gambar ini
       - Tekan S             : skip gambar ini (tidak disimpan)
       - Tekan Q             : keluar

  Output: file .txt per gambar dalam format YOLOv8 (normalized)
=============================================================
"""

import cv2
import os
import glob
import sys
from pathlib import Path

# ─── Path ─────────────────────────────────────────────────────────────────────
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR    = os.path.dirname(BASE_DIR)
DATASHEET_DIR = os.path.join(PARENT_DIR, "Datasheet")

IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
WINDOW   = "Label Manual — Anti Drone Turret"

# ─── State drawing ───────────────────────────────────────────────────────────
drawing   = False
ix, iy    = -1, -1
boxes     = []      # list of (x1, y1, x2, y2) dalam pixel
cur_box   = None    # box yang sedang di-drag
disp_frame = None   # frame tampilan saat ini
orig_frame = None   # frame asli (tidak di-modifikasi)


# ════════════════════════════════════════════════════════════════════════════════
#  Mouse callback
# ════════════════════════════════════════════════════════════════════════════════
def mouse_callback(event, x, y, flags, param):
    global drawing, ix, iy, cur_box, disp_frame

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy  = x, y
        cur_box = None

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            cur_box    = (ix, iy, x, y)
            disp_frame = draw_boxes(orig_frame.copy(), boxes, cur_box)
            cv2.imshow(WINDOW, disp_frame)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        x1, y1 = min(ix, x), min(iy, y)
        x2, y2 = max(ix, x), max(iy, y)
        if abs(x2 - x1) > 5 and abs(y2 - y1) > 5:  # abaikan klik tanpa drag
            boxes.append((x1, y1, x2, y2))
        cur_box    = None
        disp_frame = draw_boxes(orig_frame.copy(), boxes, None)
        cv2.imshow(WINDOW, disp_frame)

# Made by Zmc18-Robotics ~ @mc.zminecrafter_18 ~ Zmc18_Roboticz
# ════════════════════════════════════════════════════════════════════════════════
#  Gambar semua bounding box di frame
# ════════════════════════════════════════════════════════════════════════════════
def draw_boxes(frame, boxes_list, live_box=None):
    for i, (x1, y1, x2, y2) in enumerate(boxes_list):
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, f"Box {i+1}", (x1 + 4, y1 + 18),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 2)

    if live_box:
        lx1, ly1, lx2, ly2 = live_box
        x1, y1 = min(lx1, lx2), min(ly1, ly2)
        x2, y2 = max(lx1, lx2), max(ly1, ly2)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 200, 255), 2)

    # Panduan keyboard di pojok bawah
    h, w = frame.shape[:2]
    guide = "ENTER/SPACE:Simpan  C:Undo  R:Reset  S:Skip  Q:Keluar"
    cv2.rectangle(frame, (0, h - 30), (w, h), (20, 20, 20), -1)
    cv2.putText(frame, guide, (8, h - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.42, (200, 200, 200), 1)

    # Info jumlah box
    info = f"Boxes: {len(boxes_list)}"
    cv2.putText(frame, info, (8, 24),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    return frame


# ════════════════════════════════════════════════════════════════════════════════
#  Simpan label ke .txt (format YOLO normalized)
# ════════════════════════════════════════════════════════════════════════════════
def save_label(img_path, boxes_list, class_idx, img_w, img_h):
    txt_path = os.path.splitext(img_path)[0] + ".txt"
    lines = []
    for (x1, y1, x2, y2) in boxes_list:
        cx = ((x1 + x2) / 2) / img_w
        cy = ((y1 + y2) / 2) / img_h
        bw = abs(x2 - x1) / img_w
        bh = abs(y2 - y1) / img_h
        lines.append(f"{class_idx} {cx:.6f} {cy:.6f} {bw:.6f} {bh:.6f}")
    with open(txt_path, "w") as f:
        f.write("\n".join(lines))
    return txt_path


# ════════════════════════════════════════════════════════════════════════════════
#  Scan semua folder kelas dari Datasheet
# ════════════════════════════════════════════════════════════════════════════════
def scan_all_classes(datasheet_dir):
    """Return list of (display_name, kelas_dir, class_idx)"""
    result = []
    dp = Path(datasheet_dir)
    if not dp.exists():
        return result

    idx = 0
    for kategori in sorted(dp.iterdir()):
        if not kategori.is_dir():
            continue
        for kelas in sorted(kategori.iterdir()):
            if not kelas.is_dir():
                continue
            display = f"{kategori.name} / {kelas.name}"
            result.append((display, str(kelas), idx))
            idx += 1
    return result


def count_images_in(folder):
    count = 0
    labeled = 0
    for f in os.listdir(folder):
        if os.path.splitext(f)[1].lower() in IMG_EXTS:
            count += 1
            txt = os.path.splitext(os.path.join(folder, f))[0] + ".txt"
            if os.path.exists(txt):
                labeled += 1
    return count, labeled


# ════════════════════════════════════════════════════════════════════════════════
#  Label satu folder
# ════════════════════════════════════════════════════════════════════════════════
def label_folder(folder_path, class_idx, skip_labeled=True):
    global boxes, disp_frame, orig_frame

    # Kumpulkan gambar
    img_files = sorted([
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if os.path.splitext(f)[1].lower() in IMG_EXTS
    ])

    if not img_files:
        print(f"  [!] Tidak ada gambar di: {folder_path}")
        return 0, 0

    cv2.namedWindow(WINDOW, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW, 900, 600)
    cv2.setMouseCallback(WINDOW, mouse_callback)

    saved  = 0
    skipped = 0
    total  = len(img_files)

    for i, img_path in enumerate(img_files):
        txt_path = os.path.splitext(img_path)[0] + ".txt"

        # Skip jika sudah dilabel dan mode skip aktif
        if skip_labeled and os.path.exists(txt_path):
            print(f"  [SKIP SUDAH LABEL] {os.path.basename(img_path)}")
            continue

        # Load gambar
        frame = cv2.imread(img_path)
        if frame is None:
            print(f"  [!] Gagal buka: {img_path}")
            continue

        img_h, img_w = frame.shape[:2]
        orig_frame   = frame.copy()
        boxes        = []

        # Set judul window
        fname = os.path.basename(img_path)
        cv2.setWindowTitle(WINDOW, f"{WINDOW}  [{i+1}/{total}]  {fname}")
# Made by Zmc18-Robotics ~ @mc.zminecrafter_18 ~ Zmc18_Roboticz
        disp_frame = draw_boxes(orig_frame.copy(), boxes, None)
        cv2.imshow(WINDOW, disp_frame)

        print(f"\n  [{i+1}/{total}] {fname}")
        print("    -> Drag untuk buat box. ENTER=simpan, C=undo, R=reset, S=skip, Q=keluar")

        done = False
        while not done:
            key = cv2.waitKey(20) & 0xFF

            # ENTER atau SPASI = simpan
            if key in (13, 32):
                if not boxes:
                    print("    [!] Belum ada box! Buat minimal 1 box dulu.")
                    continue
                out = save_label(img_path, boxes, class_idx, img_w, img_h)
                print(f"    [SAVED] {out}  ({len(boxes)} box)")
                saved += 1
                done = True

            # C = undo (hapus box terakhir)
            elif key == ord('c'):
                if boxes:
                    boxes.pop()
                    disp_frame = draw_boxes(orig_frame.copy(), boxes, None)
                    cv2.imshow(WINDOW, disp_frame)
                    print(f"    [UNDO] Tersisa {len(boxes)} box")

            # R = reset semua box
            elif key == ord('r'):
                boxes = []
                disp_frame = draw_boxes(orig_frame.copy(), boxes, None)
                cv2.imshow(WINDOW, disp_frame)
                print("    [RESET] Semua box dihapus")

            # S = skip gambar ini
            elif key == ord('s'):
                print(f"    [SKIP] {fname}")
                skipped += 1
                done = True

            # Q = keluar dari labeling
            elif key == ord('q'):
                print("\n  [KELUAR] Labeling dihentikan.")
                cv2.destroyAllWindows()
                return saved, skipped

    cv2.destroyAllWindows()
    return saved, skipped


# ════════════════════════════════════════════════════════════════════════════════
#  Main — menu pemilihan folder
# ════════════════════════════════════════════════════════════════════════════════
def main():
    print("=" * 60)
    print("  LABEL MANUAL — Anti Drone Turret System")
    print("=" * 60)
    print(f"\n  Datasheet: {DATASHEET_DIR}\n")

    if not os.path.exists(DATASHEET_DIR):
        print("[ERROR] Folder Datasheet tidak ditemukan!")
        print(f"  Buat folder: {DATASHEET_DIR}")
        print("  Lalu isi dengan foto-foto drone di sub-foldernya.")
        return

    classes = scan_all_classes(DATASHEET_DIR)

    if not classes:
        print("[ERROR] Tidak ada sub-folder kelas di Datasheet!")
        print("  Struktur yang diharapkan:")
        print("    Datasheet/")
        print("      Drone aman/")
        print("        Drone1/   <- taruh foto di sini")
        print("        Drone2/")
        print("      Drone berbahaya/")
        print("        Drone1/")
        return

    # Tampilkan menu
    print("  Pilih folder yang ingin dilabel:\n")
    print(f"  {'No.':<5} {'Folder Kelas':<45} {'Total':>6} {'Labeled':>8}")
    print("  " + "-" * 68)
    for i, (display, folder, idx) in enumerate(classes):
        total, labeled = count_images_in(folder)
        status = "✓ DONE" if (total > 0 and labeled >= total) else ""
        print(f"  [{i+1:02d}]  {display:<43} {total:>6}   {labeled:>6}   {status}")

    print(f"\n  [ALL] Label semua folder sekaligus")
    print(f"  [Q]   Keluar\n")

    choice = input("  Pilih nomor (atau ALL): ").strip().lower()

    if choice == 'q':
        return

    elif choice == 'all':
        total_saved = 0
        total_skip  = 0
        for display, folder, class_idx in classes:
            print(f"\n{'='*60}")
            print(f"  Folder: {display}  (class_idx={class_idx})")
            print(f"{'='*60}")
            s, sk = label_folder(folder, class_idx, skip_labeled=True)
            total_saved += s
            total_skip  += sk
        print(f"\n[SELESAI] Total disimpan: {total_saved} | Dilewati: {total_skip}")

    else:
        try:
            idx_choice = int(choice) - 1
            if idx_choice < 0 or idx_choice >= len(classes):
                raise ValueError
        except ValueError:
            print("[ERROR] Pilihan tidak valid.")
            return
# Made by Zmc18-Robotics ~ @mc.zminecrafter_18 ~ Zmc18_Roboticz
        display, folder, class_idx = classes[idx_choice]
        print(f"\n  Mulai label: {display}  (class_idx={class_idx})")

        # Tanya skip label yang sudah ada?
        skip_ans = input("  Skip gambar yang sudah dilabel? (y/n) [y]: ").strip().lower()
        skip_labeled = (skip_ans != 'n')

        s, sk = label_folder(folder, class_idx, skip_labeled=skip_labeled)
        print(f"\n[SELESAI] Disimpan: {s} | Dilewati: {sk}")

    print("\nSekarang jalankan: python train_yolo.py")


if __name__ == "__main__":
    main()
