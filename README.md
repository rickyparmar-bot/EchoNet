# 📡 EchoNet: Acoustic Data Protocol (v4.2)

![Version](https://img.shields.io/badge/version-4.2-blue) ![License](https://img.shields.io/badge/license-MIT-green) ![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey)

EchoNet is a high-fidelity wireless data transmission system that communicates purely through **modulated sound waves**. By bypassing traditional RF protocols, it turns standard consumer hardware into a functional acoustic modem.

## 🚀 The Core Engineering
The protocol utilizes **AFSK (Audio Frequency Shift Keying)** to encode binary packets into the acoustic domain. It is designed to be resilient against echoes and ambient noise.

- **Forward Error Correction (FEC):** Implements **Hamming (7,4)** encoding to automatically detect and correct single-bit flips in the data stream.
- **High-Freq Mode:** Operating range shifted to **8kHz - 14kHz** for improved throughput and reduced audible interference.
- **Real-time Visualization:** Integrated Matplotlib-based Spectrogram for live signal monitoring.

---

## 💻 Installation & Usage

### Setup
```bash
pip install numpy sounddevice scipy python-dotenv
```

### 1. The Watcher (Visualizer)
See the data waterfall in real-time.
```bash
python3 visualizer.py
```

### 2. The Receiver (Always Listen)
Run the demodulator next. It will calibrate the noise floor and wait for a signal.
```bash
python3 demodulator.py
```

### 2. The Transmitter (Broadcast)
Send a message from another terminal or another device.
```bash
python3 modulator.py "HELLO WORLD"
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
├── modulator.py    # Binary to Audio signal generator (Hamming FEC)
├── demodulator.py  # Audio to Binary decoder (Error Correction)
├── visualizer.py   # Real-time Spectrogram monitor [NEW]
├── echotalk.py     # Interactive chat interface
├── README.md       # Technical documentation
└── .env            # Configuration secrets
```

## 🗺️ Roadmap
- [ ] **Acoustic Mesh Networking:** Auto-routing packets between multiple devices.
- [ ] **Adaptive Bitrate:** Dynamically adjusting speed based on room acoustics.
- [ ] **Quadrature Amplitude Modulation (QAM):** Increasing bandwidth by using phase shifts.

---
