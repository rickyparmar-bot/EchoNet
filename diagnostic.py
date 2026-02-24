import numpy as np
import sounddevice as sd
from scipy.fft import rfft, rfftfreq
import time

FS = 44100
DURATION = 0.5 # Analysis window

def get_peak_frequency(data):
    window = np.hamming(len(data))
    yf = rfft(data * window)
    xf = rfftfreq(len(data), 1/FS)
    idx = np.argmax(np.abs(yf))
    magnitude = np.abs(yf[idx])
    return xf[idx], magnitude

print("🔍 EchoNet Diagnostic Tool")
print("I will print the loudest frequency I hear every 0.5 seconds.")
print("Make some noise or play the modulator to see if I react!")
print("Press Ctrl+C to stop.
")

try:
    while True:
        recording = sd.rec(int(FS * DURATION), samplerate=FS, channels=1)
        sd.wait()
        recording = recording.flatten()
        peak, mag = get_peak_frequency(recording)
        
        # Simple meter
        meter = "#" * int(min(mag / 2, 50))
        print(f"Freq: {int(peak):5} Hz | Mag: {mag:8.2f} | {meter}")
except KeyboardInterrupt:
    print("
Stopped.")
