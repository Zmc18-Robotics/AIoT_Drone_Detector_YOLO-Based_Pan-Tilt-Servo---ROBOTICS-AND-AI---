# 🛡️ Anti Drone Turret Systems

Real-time drone detection system using **ESP32-CAM + YOLOv8**.  
The camera streams live to Python, where YOLO classifies whether a drone is **safe** or **dangerous**.

---

## 📁 Folder Structure

```
Anti Drone Turret Systems/
│
├── Esp32-CAM/
│   └── Esp32_CAM.ino          <- Arduino code for ESP32-CAM + flashlight
│
├── Python/
│   ├── main_yolo.py           <- Main program: streaming + detection + screenshot
│   ├── train_yolo.py          <- YOLOv8 model training from dataset
│   ├── label_manual.py        <- Bounding box labeling tool (GUI)
│   ├── screenshots/           <- Manual/auto screenshot results (S / A)
│   ├── yolo_dataset/          <- Temporary dataset during training (auto-created)
│   └── drone_model/           <- Trained model output (auto-created)
│       └── weights/
│           └── best.pt        <- Ready-to-use model
│
└── Datasheet/                 <- Dataset photo folder
    ├── Safe Drone/
    │   ├── Drone1/            <- Safe drone type 1 photos
    │   ├── Drone2/            <- Safe drone type 2 photos
    │   └── ...
    └── Dangerous Drone/
        ├── Drone1/            <- Dangerous drone type 1 photos
        ├── Drone2/            <- Dangerous drone type 2 photos
        └── ...
```

---

## ⚙️ Hardware

| Component | Details |
|---|---|
| Microcontroller | ESP32-CAM (AI-THINKER) |
| Camera | OV2640 (built-in on ESP32-CAM) |
| Flashlight / Flash | GPIO 4 (built-in flash LED) |
| Power | 5V via USB / adapter |
| Connection | WiFi 2.4 GHz |

### ESP32-CAM Pin Configuration (AI-THINKER)
Already configured in `Esp32_CAM.ino` — no changes needed as long as you're using the AI-THINKER board.

---

## 🚀 Getting Started

### 1. Upload Firmware to ESP32-CAM

1. Open **Arduino IDE**
2. Install the required libraries:
   - `WebSockets by Markus Sattler`
   - `ArduinoJson by Benoit Blanchon`
   - `ESP32 Camera` (already included in the esp32 board package)
3. Select board: `AI Thinker ESP32-CAM`
4. Edit WiFi configuration in `Esp32_CAM.ino`:
   ```cpp
   #define WIFI_SSID   "YourWiFiName"
   #define WIFI_PASS   "YourWiFiPassword"
   ```
5. Upload the sketch
6. Open Serial Monitor (115200 baud) → note the IP address displayed

---

### 2. Install Python Dependencies

```bash
pip install ultralytics opencv-python websocket-client numpy
```

---

### 3. Run the Stream (Without Training First)

Edit the IP in `Python/main_yolo.py`:
```python
CAM_IP = "192.168.x.xxx"   # Replace with your ESP32-CAM IP address
```

Run:
```bash
cd "Anti Drone Turret Systems/Python"
python main_yolo.py
```

> The program will run in **screenshot mode** — use this to collect drone dataset photos.

**Keyboard Controls:**

| Key | Function |
|---|---|
| `S` | Manual screenshot (saved to `screenshots/manual/`) |
| `A` | Toggle auto-capture (saves automatically every frame) |
| `F` | Toggle flashlight ON/OFF |
| `Q` | Quit |

---

## 📸 Dataset Collection & Training Workflow

```
[STEP 1] Collect drone photos
   └─ Run main_yolo.py → press S or A
   └─ Move photos to Datasheet/Safe Drone/Drone1/ or Dangerous Drone/Drone1/

[STEP 2] Add bounding box labels
   └─ python label_manual.py
   └─ Select folder → click+drag over drone → press ENTER

[STEP 3] Train the model
   └─ python train_yolo.py
   └─ Wait until complete (model saved to drone_model/weights/best.pt)

[STEP 4] Real-time detection
   └─ python main_yolo.py
   └─ Model loads automatically → drone detected with bounding box
```

---

## 🏷️ How to Use label_manual.py

```bash
python label_manual.py
```

1. Select a folder number from the menu (or `ALL` to process all at once)
2. For each photo:
   - **Click + Drag** over the drone object → draw a bounding box
   - You can draw **more than 1 box** per image if multiple drones are present
3. Controls:

| Key | Function |
|---|---|
| `ENTER` / `SPACE` | Save label & move to next photo |
| `C` | Undo (delete last box) |
| `R` | Reset all boxes on this photo |
| `S` | Skip this photo (not saved) |
| `Q` | Quit labeling |

---

## 🤖 Adding a New Drone Class

### In the Datasheet folder:
```
Datasheet/
  Safe Drone/
    DJI_Mini/       <- add new sub-folder
    DJI_Air/
  Dangerous Drone/
    FPV_Racer/
    Custom_Drone/
```

### In `main_yolo.py`, add a new entry:
```python
DRONE_INFO = {
    "Safe_Drone_DJI_Mini": {
        "category": "SAFE",
        "color":    (0, 200, 0),
        "action":   "Allow to pass",
    },
    "Dangerous_Drone_FPV_Racer": {
        "category": "DANGEROUS",
        "color":    (0, 0, 255),
        "action":   "ACTIVATE TURRET",
    },
}
```
> Class names are automatically formed from: `CategoryName_SubFolderName` (spaces replaced with `_`)

---

## 📌 Dataset Tips

| Condition | Recommendation |
|---|---|
| Photos per class | Minimum **50–100** photos |
| Angle variation | Photos from front, side, top, bottom |
| Distance variation | Close (< 5m), medium (5–20m), far (> 20m) |
| Lighting variation | Daytime, night (with flashlight), overcast |
| Background | Varied (sky, trees, buildings) |

---

## 🔧 Troubleshooting

| Problem | Solution |
|---|---|
| `Connection refused` | Make sure the ESP32-CAM IP is correct and on the same WiFi network |
| `Camera init failed` | Try re-uploading firmware, make sure GPIO 4 is not grounded |
| `Model not found` | Run `train_yolo.py` first after you have a labeled dataset |
| Slow frames / lag | Reduce resolution in `Esp32_CAM.ino`: change `FRAMESIZE_QVGA` to `FRAMESIZE_QQVGA` |
| YOLO is slow | Make sure `imgsz=320` in `main_yolo.py`, or use `yolov8n.pt` (nano) |

---

## 📄Documentations

<img width="472" height="326" alt="WhatsApp Image 2026-05-30 at 00 14 09" src="https://github.com/user-attachments/assets/9c7dac5c-608e-4473-86ca-36e3c7184809" />

<img width="780" height="1052" alt="WhatsApp Image 2026-05-30 at 00 14 09 (1)" src="https://github.com/user-attachments/assets/a5b63d16-2c3f-4b71-8987-8b9189f3397b" />

<img width="2250" height="1500" alt="BoxF1_curve" src="https://github.com/user-attachments/assets/b9285212-4073-446e-ac2d-306f0c7f1a65" />

<img width="3000" height="2250" alt="confusion_matrix_normalized" src="https://github.com/user-attachments/assets/e14305c7-23a2-4752-ba5a-364b4b038777" />

<img width="2400" height="1200" alt="results" src="https://github.com/user-attachments/assets/4977a5fa-59a1-4234-ac15-ffc0ff2d4e55" />

<img width="1408" height="1024" alt="val_batch0_pred" src="https://github.com/user-attachments/assets/23806231-929d-4f32-848c-0143a5d4edd8" />


---

*Project: Anti Drone Turret Systems | Platform: ESP32-CAM + YOLOv8 + Python*
