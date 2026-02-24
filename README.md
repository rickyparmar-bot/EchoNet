# EchoNet: Acoustic Data Transmission Protocol 📡🔊

EchoNet is a high-level engineering project designed for the **MIT Maker Portfolio**. It implements a robust "Air-Gapped" communication protocol that allows two computers to exchange data using only their speakers and microphones.

## 🚀 Overview
Traditional wireless communication (WiFi, Bluetooth) relies on radio frequencies. EchoNet operates in the acoustic spectrum, utilizing Digital Signal Processing (DSP) to turn sound waves into a reliable data link.

### Key Features:
*   **BFSK Modulation:** Binary Frequency Shift Keying using orthogonal frequencies to minimize interference.
*   **Hamming (7,4) Error Correction:** Automatically detects and repairs single-bit errors caused by background noise.
*   **Echo Mitigation:** Implements a "GAP Frequency" protocol to flush acoustic reflections in high-reverb environments.
*   **Hardware-Agnostic:** Runs on standard laptop hardware with no specialized sensors required.

## 🛠️ Tech Stack
*   **Language:** Python 3.x
*   **Libraries:** NumPy, SciPy (FFT Analysis), SoundDevice (PortAudio), SoundFile.
*   **Protocol:** Custom-built clocked acoustic frame format.

## 🧪 Verification
The protocol has been mathematically verified using a virtual loopback simulation with 10% additive white Gaussian noise (AWGN), achieving **100% data integrity**.

## 📖 Usage
1. **Listener:** `python demodulator.py`
2. **Sender:** `python modulator.py "Your Message"`

---
*Developed as part of a series of unconventional computing and low-level systems projects for the MIT 2026 Admissions cycle.*
