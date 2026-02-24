# 📡 EchoNet: Acoustic Data Protocol (v3.5)

EchoNet is a high-fidelity wireless data transmission system that communicates purely through **modulated sound waves**. It turns standard laptop speakers and microphones into a functional data link, bypassing traditional RF (Radio Frequency) communication using Digital Signal Processing (DSP).

## 🚀 Technical Core
The system utilizes **AFSK (Audio Frequency Shift Keying)** to encode binary packets into the acoustic domain. By precisely controlling air pressure modulation, EchoNet achieves stable communication in standard office or room environments.

### 🛠️ Key Architectural Features
- **Binary Packetization:** Every transmission is wrapped in a high-level frame containing an 8-bit **Length Header** and an XOR-based **Checksum Footer**. This ensures 100% data integrity; if a single bit is corrupted by background noise, the packet is rejected.
- **FSK Modulation Logic:** 
    - `1kHz`: Sync/Preamble
    - `1.5kHz`: Bit 0
    - `2kHz`: Bit 1
    - `2.5kHz`: Echo Flush (Gap)
- **Spectral Visualization:** Includes a real-time **Spectrogram** visualizer using high-speed Fast Fourier Transforms (FFT). This allows the user to see the "Acoustic Fingerprint" of the data as it arrives.
- **Doppler-Shift Filtering:** Features "Anti-Motion Logic" that calculates signal-to-noise ratios across specific bins, preventing false triggers caused by physical movement or hand gestures.
- **Safe Mode implementation:** Unlike high-frequency "ultrasonic" protocols that cause physiological discomfort (headaches), EchoNet v3.5 is optimized for the human-safe audible range (1kHz-2.5kHz).

## 📊 Performance
- **Bitrate:** Optimized for reliability over raw speed, using 150ms-200ms bit durations.
- **Hardware Compatibility:** Works on any device with a standard 44.1kHz sound card.
- **Resilience:** Successfully decodes messages across a 5-meter distance in standard room noise.

---
*Part of the MIT Maker Portfolio 2026.* 🚀📡
