# Driver Monitoring System (DMS)

**Driver Monitoring System (DMS)** is a real-time AI application that monitors a driver's alertness using a webcam. It detects **drowsiness**  by monitoring **eye closure**, **yawning**  using mouth movement, and allows the driver to **silence the alarm with a thumbs-up gesture**.

The project is powered by **MediaPipe Face Mesh** and **MediaPipe Hands** for landmark detection, **OpenCV** for real-time video processing, and **Pygame** for alarm playback.

The Driver Monitoring System is built around a straightforward premise: a camera watches the driver, and software watches the camera. What happens in between those two steps is where the complexity lives. The system is a Python script that opens the webcam and processes each frame in a loop. For every frame, it checks for **eyes closed, mouth open and thumbs up**. When any check triggers, it shows a **text overlay** on the video window and plays **audio alert**. There is no backend, database, or network connection. All state is held in memory and resets when the script exits.

---

#  Demo

>  The application opens a single webcam window displaying:
>
> *  Live camera feed
> *  Face Mesh and Hand Landmarks
> *  Real-time EAR (Eye Aspect Ratio) and MAR (Mouth Aspect Ratio)
> *  Driver status
> *  Yawn counter
> *  Alarm notifications

Press **Q** anytime to exit the application.

Press **V** to toggle Face Mesh and Hand Mesh visualization.

---

# 🧠 Features

*  Real-time webcam monitoring
*  Detects prolonged eye closure (drowsiness)
*  Detects continuous yawning
*  Smooth EAR and MAR calculations to reduce false detections
*  Automatic alarm when drowsiness is detected
*  Hold a thumbs-up gesture for 1 second to stop the alarm
*  Alarm automatically stops after 25 seconds
*  Toggle facial and hand landmarks on/off
*  Runs completely offline (No cloud APIs required)

---

# 🧬 Technologies Used

* Python
* OpenCV
* MediaPipe Face Mesh
* MediaPipe Hands
* NumPy
* Pygame

---

# 📦 Requirements

* **Python 3.12.x**
  *(MediaPipe 0.10.9 is recommended for maximum compatibility.)*

* Webcam

* Windows, macOS or Linux

---

# 🗂️ Project Structure

```text
DMS/
│
├── assets/
│   └── samsung alarm.mp3
│
├── output/
│
├── dms.py
├── README.md
└── requirements.txt
```

---

# 🚀 How To Use

## 1️⃣ Clone the Repository

Open Command Prompt, PowerShell or Terminal.

```bash
git clone https://github.com/<HariSharmaa>/Driver-Monitoring-system.git
cd Driver-Monitoring-System
```

---

## 2️⃣ Install Python 3.12

Download Python from the official website:

https://www.python.org/downloads/release/python-3126/

During installation:

* ✅ Add Python to PATH
* ✅ Click **Install Now**

Verify installation:

```bash
python --version
```

---

## 3️⃣ Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it.

**Windows**

```bash
.venv\Scripts\activate
```

**macOS / Linux**

```bash
source .venv/bin/activate
```

---

## 4️⃣ Install Dependencies

```bash
pip install opencv-python mediapipe==0.10.9 pygame numpy
```

---

## 5️⃣ Run the Project

```bash
python dms.py
```

---


# 🖥️ Controls

| Key   | Action                       |
| ----- | ---------------------------- |
| **Q** | Quit the application         |
| **V** | Toggle Face Mesh & Hand Mesh |

---

# 🚨 Detection Logic

### 😴 Drowsiness Detection

* Calculates Eye Aspect Ratio (EAR)
* If both eyes remain closed for more than **2 seconds**, the driver is marked as **SLEEPY**
* Alarm starts automatically

---

### 🥱 Yawn Detection

* Calculates Mouth Aspect Ratio (MAR)
* A mouth open for more than **2 seconds** counts as one yawn
* Alarm activates after **3 yawns**

---

### 👍 Alarm Reset

Once the alarm is active:

* Show a 👍 thumbs-up gesture
* Hold it for **1 second**
* Alarm stops and driver status returns to **NORMAL**

---

# 🧮 Troubleshooting

| Problem                                | Solution                                                                  |
| -------------------------------------- | ------------------------------------------------------------------------- |
| Camera not opening                     | Ensure no other application is using the webcam.                          |
| No matching distribution for MediaPipe | Install Python 3.12 and MediaPipe 0.10.9.                                 |
| Alarm not playing                      | Verify `samsung alarm.mp3` exists and the filename matches the code.      |
| Face landmarks not detected            | Improve lighting and face the camera directly.                            |
| Thumbs-up not detected                 | Hold your hand fully inside the camera frame and keep the gesture steady. |

---

# 💡 Future Improvements

*  SMS or Email notification when driver becomes drowsy
*  Head pose estimation
*  GPS location sharing during emergencies
*  Driver fatigue analytics dashboard
*  Voice-based alarm dismissal
*  Night mode optimization using IR cameras
*  TensorFlow model for advanced fatigue prediction

---

# 📚 Libraries Used

* OpenCV
* MediaPipe
* NumPy
* Pygame

---

## ⭐ If you found this project helpful, consider giving the repository a star!
