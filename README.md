# 📡 EchoNet: Acoustic Data Protocol (v3.5)

![Version](https://img.shields.io/badge/version-3.5-blue) ![License](https://img.shields.io/badge/license-MIT-green) ![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey)

EchoNet is a high-fidelity wireless data transmission system that communicates purely through **modulated sound waves**. By bypassing traditional RF protocols, it turns standard consumer hardware into a functional acoustic modem.

## 🚀 The Core Engineering
The protocol utilizes **AFSK (Audio Frequency Shift Keying)** to encode binary packets into the acoustic domain. It is designed to be resilient against echoes and ambient noise.

### 🛠️ Key Architectural Pillars
- **Frame Structure:** Every packet contains a sync preamble, an 8-bit length header, the payload, and an XOR-based checksum.
- **Anti-Motion Logic:** Utilizes high-resolution FFT analysis to filter out Doppler-shift interference caused by movement in the physical environment.
- **Safe Mode:** Operating range constrained to **1kHz - 2.5kHz** to ensure maximum hardware compatibility and zero physiological discomfort.

---

## 💻 Installation & Usage

### Setup
```bash
pip install numpy sounddevice scipy python-dotenv
```

### 1. The Receiver (Always Listen)
Run the demodulator first. It will calibrate the noise floor and wait for a signal.
```bash
python3 demodulator.py
```

### 2. The Transmitter (Broadcast)
Send a message from another terminal or another device.
```bash
python3 modulator.py "MIT 2026"
```

### 3. Acoustic Chat (Two-Way)
Launch the interactive "Walkie-Talkie" app.
```bash
python3 echotalk.py
```

---

## 📂 Project Structure
```text
EchoNet/
├── modulator.py    # Binary to Audio signal generator
├── demodulator.py  # Audio to Binary decoder (FFT based)
├── echotalk.py     # Interactive chat interface
├── README.md       # Technical documentation
└── .env            # Configuration secrets
```

## 🗺️ Roadmap
- [ ] **Acoustic Mesh Networking:** Auto-routing packets between multiple devices.
- [ ] **Adaptive Bitrate:** Dynamically adjusting speed based on room acoustics.
- [ ] **Quadrature Amplitude Modulation (QAM):** Increasing bandwidth by using phase shifts.

---
