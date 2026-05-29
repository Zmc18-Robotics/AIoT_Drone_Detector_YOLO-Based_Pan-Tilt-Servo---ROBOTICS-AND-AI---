#include <ESP32Servo.h>
#include <WebServer.h>
#include <WiFi.h>

// =======================================================
// KONFIGURASI WIFI
// =======================================================
const char *ssid = "Absolute Solver";
const char *password = "CynIsMyRobo18z";

// =======================================================
// KONFIGURASI PIN SERVO
// =======================================================
// Sesuaikan pin dengan yang Anda gunakan di ESP32
// Menyesuaikan dengan wiring di project Medical Waste agar langsung jalan tanpa mengubah kabel
const int panPin = 33;  // Servo 1: Kanan - Kiri (Pan)
const int tiltPin = 19; // Servo 2: Atas - Bawah (Tilt)

Servo servoPan;
Servo servoTilt;

WebServer server(80);

// Nilai awal posisi servo (di tengah)
int panAngle = 90;
int tiltAngle = 90;

// Status Auto Tracking
bool autoTrackingEnabled = false;

// =======================================================
// HALAMAN WEB UI (HTML + CSS + JS)
// =======================================================
// Menggunakan desain modern dan dark mode
const char *htmlPage = R"rawliteral(
<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Turret Servo Web IoT</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    body {
      font-family: 'Inter', sans-serif;
      background-color: #0f172a;
      color: #f8fafc;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100vh;
      margin: 0;
    }
    .card {
      background: #1e293b;
      padding: 30px;
      border-radius: 20px;
      box-shadow: 0 20px 40px rgba(0,0,0,0.4);
      width: 85%;
      max-width: 400px;
      border: 1px solid #334155;
    }
    h1 {
      margin-top: 0;
      color: #38bdf8;
      font-size: 26px;
      text-align: center;
      text-transform: uppercase;
      letter-spacing: 1px;
    }
    .status {
      text-align: center;
      font-size: 14px;
      color: #94a3b8;
      margin-bottom: 30px;
    }
    .slider-container {
      margin: 25px 0;
      background: #0f172a;
      padding: 20px;
      border-radius: 15px;
      border: 1px solid #1e293b;
    }
    .slider-label {
      display: flex;
      justify-content: space-between;
      margin-bottom: 15px;
      font-weight: 600;
      font-size: 16px;
      color: #e2e8f0;
    }
    .value-badge {
      background: #38bdf8;
      color: #0f172a;
      padding: 2px 10px;
      border-radius: 12px;
      font-size: 14px;
      font-weight: 800;
    }
    input[type=range] {
      -webkit-appearance: none;
      width: 100%;
      background: transparent;
    }
    input[type=range]:focus {
      outline: none;
    }
    input[type=range]::-webkit-slider-runnable-track {
      width: 100%;
      height: 10px;
      cursor: pointer;
      background: #334155;
      border-radius: 5px;
      transition: 0.2s;
    }
    input[type=range]:hover::-webkit-slider-runnable-track {
      background: #475569;
    }
    input[type=range]::-webkit-slider-thumb {
      height: 28px;
      width: 28px;
      border-radius: 50%;
      background: #38bdf8;
      cursor: pointer;
      -webkit-appearance: none;
      margin-top: -9px;
      box-shadow: 0 0 15px rgba(56, 189, 248, 0.4);
      transition: all 0.2s;
      border: 3px solid #0f172a;
    }
    input[type=range]::-webkit-slider-thumb:hover {
      transform: scale(1.15);
      box-shadow: 0 0 20px rgba(56, 189, 248, 0.6);
    }
    input[type=range]::-webkit-slider-thumb:active {
      transform: scale(1.25);
      background: #7dd3fc;
    }
    .btn-reset {
      background: #334155;
      color: #f8fafc;
      border: 1px solid #475569;
      padding: 12px 20px;
      border-radius: 12px;
      font-size: 15px;
      font-weight: 600;
      cursor: pointer;
      width: 100%;
      margin-top: 10px;
      transition: all 0.2s;
      font-family: 'Inter', sans-serif;
    }
    .btn-reset:hover {
      background: #475569;
      border-color: #94a3b8;
    }
    .btn-reset:active {
      transform: scale(0.98);
      background: #1e293b;
    }
    .switch {
      position: relative;
      display: inline-block;
      width: 50px;
      height: 24px;
    }
    .switch input { 
      opacity: 0;
      width: 0;
      height: 0;
    }
    .slider-toggle {
      position: absolute;
      cursor: pointer;
      top: 0; left: 0; right: 0; bottom: 0;
      background-color: #334155;
      transition: .4s;
      border-radius: 24px;
    }
    .slider-toggle:before {
      position: absolute;
      content: "";
      height: 18px;
      width: 18px;
      left: 3px;
      bottom: 3px;
      background-color: #f8fafc;
      transition: .4s;
      border-radius: 50%;
    }
    input:checked + .slider-toggle {
      background-color: #22d55a;
    }
    input:checked + .slider-toggle:before {
      transform: translateX(26px);
    }
  </style>
</head>
<body>
  <div class="card">
    <h1>Turret Control</h1>
    <div class="status">Live Servo Web IoT Dashboard</div>

    <div style="display:flex; justify-content:space-between; align-items:center; background:#0f172a; padding:15px; border-radius:12px; border:1px solid #1e293b; margin-bottom:20px;">
      <span style="font-weight:600; font-size:15px;">🤖 Auto Tracking (Python)</span>
      <label class="switch">
        <input type="checkbox" id="trackingToggle" onchange="toggleTracking(this.checked)">
        <span class="slider-toggle"></span>
      </label>
    </div>

    <div class="slider-container">
      <div class="slider-label">
        <span>Servo 1 (Kanan-Kiri)</span>
        <span class="value-badge" id="panValue">90&deg;</span>
      </div>
      <input type="range" min="0" max="180" value="90" id="panSlider" oninput="updateServo('pan', this.value)">
    </div>
    
    <div class="slider-container">
      <div class="slider-label">
        <span>Servo 2 (Atas-Bawah)</span>
        <span class="value-badge" id="tiltValue">90&deg;</span>
      </div>
      <input type="range" min="0" max="180" value="90" id="tiltSlider" oninput="updateServo('tilt', this.value)">
    </div>
    
    <button class="btn-reset" onclick="resetToCenter()">&#8634; Reset ke Posisi Tengah (90&deg;)</button>
  </div>

  <script>
    let lastSendTime = {};
    let pendingValue = {};
    let debounceTimer = {};

    function toggleTracking(state) {
      var xhr = new XMLHttpRequest();
      xhr.open("GET", "/toggleTracking?state=" + (state ? "true" : "false"), true);
      xhr.send();
    }

    function sendToESP(type, value) {
      var xhr = new XMLHttpRequest();
      xhr.open("GET", "/set?servo=" + type + "&angle=" + value, true);
      xhr.send();
    }

    function updateServo(type, value) {
      // Perbarui angka di layar secara langsung
      document.getElementById(type + "Value").innerHTML = value + "&deg;";
      pendingValue[type] = value;
      
      let now = Date.now();
      
      // Throttle: Kirim perintah maksimal setiap 80ms agar gerakan "Live" & mulus, tanpa membuat ESP32 macet
      if (!lastSendTime[type] || now - lastSendTime[type] > 80) {
        sendToESP(type, pendingValue[type]);
        lastSendTime[type] = now;
      } else {
        // Pastikan posisi terakhir saat jari dilepas tetap terkirim
        clearTimeout(debounceTimer[type]);
        debounceTimer[type] = setTimeout(() => {
          sendToESP(type, pendingValue[type]);
          lastSendTime[type] = Date.now();
        }, 80);
      }
    }

    function resetToCenter() {
      // Kembalikan slider ke tengah
      document.getElementById("panSlider").value = 90;
      document.getElementById("tiltSlider").value = 90;
      
      // Update angka di UI
      document.getElementById("panValue").innerHTML = "90&deg;";
      document.getElementById("tiltValue").innerHTML = "90&deg;";
      
      // Kirim perintah reset
      sendToESP('pan', 90);
      
      // Beri jeda 100ms agar ESP32 tidak menerima 2 request bersamaan yang bisa membuatnya macet
      setTimeout(() => {
        sendToESP('tilt', 90);
      }, 100);
    }
  </script>
</body>
</html>
)rawliteral";

// =======================================================
// HANDLER ROUTING WEB
// =======================================================
void handleRoot() { server.send(200, "text/html", htmlPage); }

void handleToggleTracking() {
  if (server.hasArg("state")) {
    autoTrackingEnabled = (server.arg("state") == "true");
    Serial.print("[SISTEM] Auto Tracking kini: ");
    Serial.println(autoTrackingEnabled ? "ON" : "OFF");
    server.send(200, "text/plain", "OK");
  } else {
    server.send(400, "text/plain", "Bad Request");
  }
}

void handleTrack() {
  // Jika auto tracking mati, abaikan perintah dari Python
  if (!autoTrackingEnabled) {
    server.send(200, "text/plain", "IGNORED");
    return;
  }
  
  if (server.hasArg("pan") && server.hasArg("tilt")) {
    int pan = server.arg("pan").toInt();
    int tilt = server.arg("tilt").toInt();
    
    panAngle = constrain(pan, 0, 180);
    tiltAngle = constrain(tilt, 0, 180);
    
    servoPan.write(panAngle);
    servoTilt.write(tiltAngle);
    
    server.send(200, "text/plain", "OK");
  } else {
    server.send(400, "text/plain", "Bad Request");
  }
}

void handleSetServo() {
  if (server.hasArg("servo") && server.hasArg("angle")) {
    String servoType = server.arg("servo");
    int angle = server.arg("angle").toInt();

    if (servoType == "pan") {
      panAngle = angle;
      servoPan.write(panAngle);
      Serial.print("Pan (Kanan-Kiri) bergerak ke: ");
      Serial.println(panAngle);
    } else if (servoType == "tilt") {
      tiltAngle = angle;
      servoTilt.write(tiltAngle);
      Serial.print("Tilt (Atas-Bawah) bergerak ke: ");
      Serial.println(tiltAngle);
    }
    server.send(200, "text/plain", "OK");
  } else {
    server.send(400, "text/plain", "Bad Request");
  }
}

// =======================================================
// SETUP AWAL
// =======================================================
void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("\n[SISTEM] Menginisialisasi Servo...");

  // Wajib untuk library ESP32Servo: Alokasikan hardware timer untuk PWM ESP32
  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  ESP32PWM::allocateTimer(2);
  ESP32PWM::allocateTimer(3);

  // Konfigurasi pin PWM untuk ESP32Servo
  // ESP32 membutuhkan penyesuaian frekuensi (50Hz untuk standard servo)
  servoPan.setPeriodHertz(50);
  servoPan.attach(panPin, 500, 2400); // 500us - 2400us adalah rentang umum servo
  delay(20);

  servoTilt.setPeriodHertz(50);
  servoTilt.attach(tiltPin, 500, 2400);
  delay(20);

  // Set posisi awal ke tengah (90 derajat)
  servoPan.write(panAngle);
  servoTilt.write(tiltAngle);
  delay(200);

  // Mulai koneksi WiFi
  Serial.print("[SISTEM] Menghubungkan ke WiFi: ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[SISTEM] WiFi Berhasil Terhubung!");
    Serial.print(
        "[SISTEM] Buka IP Address berikut di Browser HP/Laptop Anda: http://");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println(
        "\n[ERROR] Gagal terhubung ke WiFi. Silakan cek SSID dan Password.");
  }

  // Daftarkan route untuk web server
  server.on("/", handleRoot);
  server.on("/set", handleSetServo);
  server.on("/toggleTracking", handleToggleTracking);
  server.on("/track", handleTrack);

  // Jalankan server
  server.begin();
  Serial.println("[SISTEM] Web Server IoT Turret siap digunakan!");
}

// =======================================================
// MAIN LOOP
// =======================================================
void loop() {
  // Tangani request dari client/browser
  server.handleClient();
}
