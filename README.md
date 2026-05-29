# 🛡️ Anti Drone Turret Systems

Sistem deteksi drone real-time menggunakan **ESP32-CAM + YOLOv8**.  
Kamera stream langsung ke Python, lalu YOLO mengklasifikasikan apakah drone **aman** atau **berbahaya**.

---

## 📁 Struktur Folder

```
Anti Drone Turret Systems/
│
├── Esp32-CAM/
│   └── Esp32_CAM.ino          <- Kode Arduino untuk ESP32-CAM + senter
│
├── Python/
│   ├── main_yolo.py           <- Program utama: streaming + deteksi + screenshot
│   ├── train_yolo.py          <- Training model YOLOv8 dari dataset
│   ├── label_manual.py        <- Tool labeling bounding box (GUI)
│   ├── screenshots/           <- Hasil screenshot manual/auto (S / A)
│   ├── yolo_dataset/          <- Dataset sementara saat training (auto-dibuat)
│   └── drone_model/           <- Model hasil training (auto-dibuat)
│       └── weights/
│           └── best.pt        <- Model siap pakai
│
└── Datasheet/                 <- Folder foto dataset
    ├── Drone aman/
    │   ├── Drone1/            <- Foto-foto drone aman tipe 1
    │   ├── Drone2/            <- Foto-foto drone aman tipe 2
    │   └── ...
    └── Drone berbahaya/
        ├── Drone1/            <- Foto-foto drone berbahaya tipe 1
        ├── Drone2/            <- Foto-foto drone berbahaya tipe 2
        └── ...
```

---

## ⚙️ Hardware

| Komponen | Detail |
|---|---|
| Mikrokontroler | ESP32-CAM (AI-THINKER) |
| Kamera | OV2640 (sudah built-in di ESP32-CAM) |
| Senter / Flash | GPIO 4 (built-in flash LED) |
| Power | 5V via USB / adaptor |
| Koneksi | WiFi 2.4 GHz |

### Pin ESP32-CAM (AI-THINKER)
Sudah terkonfigurasi di dalam `Esp32_CAM.ino` — tidak perlu diubah selama menggunakan board AI-THINKER.

---

## 🚀 Cara Memulai

### 1. Upload Firmware ke ESP32-CAM

1. Buka **Arduino IDE**
2. Install library yang dibutuhkan:
   - `WebSockets by Markus Sattler`
   - `ArduinoJson by Benoit Blanchon`
   - `ESP32 Camera` (sudah include di board package esp32)
3. Pilih board: `AI Thinker ESP32-CAM`
4. Edit konfigurasi WiFi di `Esp32_CAM.ino`:
   ```cpp
   #define WIFI_SSID   "NamaWiFi_Anda"
   #define WIFI_PASS   "PasswordWiFi_Anda"
   ```
5. Upload sketch
6. Buka Serial Monitor (115200 baud) → catat IP address yang muncul

---

### 2. Install Dependensi Python

```bash
pip install ultralytics opencv-python websocket-client numpy
```

---

### 3. Jalankan Stream (Tanpa Training Dulu)

Edit IP di `Python/main_yolo.py`:
```python
CAM_IP = "192.168.x.xxx"   # Ganti dengan IP ESP32-CAM Anda
```

Jalankan:
```bash
cd "Anti Drone Turret Systems/Python"
python main_yolo.py
```

> Program akan berjalan dalam **mode screenshot** — gunakan ini untuk mengumpulkan foto dataset drone.

**Kontrol keyboard:**

| Tombol | Fungsi |
|---|---|
| `S` | Screenshot manual (simpan ke `screenshots/manual/`) |
| `A` | Toggle auto-capture (simpan otomatis tiap frame) |
| `F` | Toggle senter ON/OFF |
| `Q` | Keluar |

---

## 📸 Alur Pengumpulan Dataset & Training

```
[LANGKAH 1] Kumpulkan foto drone
   └─ Jalankan main_yolo.py → tekan S atau A
   └─ Pindahkan foto ke Datasheet/Drone aman/Drone1/ atau Drone berbahaya/Drone1/

[LANGKAH 2] Beri label bounding box
   └─ python label_manual.py
   └─ Pilih folder → klik+drag di atas drone → tekan ENTER

[LANGKAH 3] Training model
   └─ python train_yolo.py
   └─ Tunggu hingga selesai (model tersimpan di drone_model/weights/best.pt)

[LANGKAH 4] Deteksi real-time
   └─ python main_yolo.py
   └─ Model otomatis dimuat → drone terdeteksi dengan bounding box
```

---

## 🏷️ Cara Menggunakan label_manual.py

```bash
python label_manual.py
```

1. Pilih nomor folder dari menu (atau `ALL` untuk semua sekaligus)
2. Untuk tiap foto:
   - **Klik + Drag** di atas objek drone → buat kotak bounding box
   - Bisa buat **lebih dari 1 box** per gambar jika ada beberapa drone
3. Kontrol:

| Tombol | Fungsi |
|---|---|
| `ENTER` / `SPASI` | Simpan label & lanjut ke foto berikutnya |
| `C` | Undo (hapus box terakhir) |
| `R` | Reset semua box di foto ini |
| `S` | Skip foto ini (tidak disimpan) |
| `Q` | Keluar dari labeling |

---

## 🤖 Menambah Kelas Drone Baru

### Di folder Datasheet:
```
Datasheet/
  Drone aman/
    DJI_Mini/       <- tambahkan sub-folder baru
    DJI_Air/
  Drone berbahaya/
    FPV_Racer/
    Custom_Drone/
```

### Di `main_yolo.py`, tambahkan entri baru:
```python
DRONE_INFO = {
    "Drone_aman_DJI_Mini": {
        "kategori": "AMAN",
        "warna":    (0, 200, 0),
        "aksi":     "Biarkan lewat",
    },
    "Drone_berbahaya_FPV_Racer": {
        "kategori": "BERBAHAYA",
        "warna":    (0, 0, 255),
        "aksi":     "AKTIFKAN TURRET",
    },
}
```
> Nama kelas otomatis dibentuk dari: `NamaKategori_NamaSubFolder` (spasi diganti `_`)

---

## 📌 Tips Dataset

| Kondisi | Rekomendasi |
|---|---|
| Jumlah foto per kelas | Minimal **50–100** foto |
| Variasi sudut | Foto dari depan, samping, atas, bawah |
| Variasi jarak | Dekat (< 5m), sedang (5–20m), jauh (> 20m) |
| Variasi cahaya | Siang, malam (dengan senter), mendung |
| Background | Bervariasi (langit, pohon, gedung) |

---

## 🔧 Troubleshooting

| Masalah | Solusi |
|---|---|
| `Connection refused` | Pastikan IP ESP32-CAM benar dan berada di jaringan WiFi yang sama |
| `Kamera gagal init` | Coba upload ulang firmware, pastikan GPIO 4 tidak di-ground |
| `Model tidak ditemukan` | Jalankan `train_yolo.py` dulu setelah punya dataset berlabel |
| Frame lambat / lag | Kurangi resolusi di `Esp32_CAM.ino`: ganti `FRAMESIZE_QVGA` ke `FRAMESIZE_QQVGA` |
| YOLO lambat | Pastikan `imgsz=320` di `main_yolo.py`, atau pakai `yolov8n.pt` (nano) |

---

*Proyek: Anti Drone Turret Systems | Platform: ESP32-CAM + YOLOv8 + Python*
