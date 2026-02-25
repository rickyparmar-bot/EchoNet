import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.fft import rfft, rfftfreq
import sys

# Parameters
FS = 44100
CHUNK_SIZE = int(FS * 0.05)  
HISTORY_LEN = 100            
TARGET_FREQS = [8000, 10000, 12000, 14000]
MAX_FREQ_PLOT = 16000

print("🎧 Starting EchoNet Visualizer...")

freq_bins = rfftfreq(CHUNK_SIZE, 1/FS)
valid_idx = np.where(freq_bins <= MAX_FREQ_PLOT)[0]

fig, ax = plt.subplots(figsize=(10, 6), facecolor='#1e1e1e')
ax.set_facecolor('#1e1e1e')

history = np.zeros((HISTORY_LEN, len(valid_idx)))

im = ax.imshow(
    history.T, 
    aspect='auto', 
    origin='lower', 
    cmap='inferno',
    extent=[0, HISTORY_LEN, 0, np.max(freq_bins[valid_idx])],
    vmin=0, vmax=1.0
)

for f in TARGET_FREQS:
    ax.axhline(f, color='cyan', alpha=0.6, linestyle='--', lw=2)
    ax.text(2, f + 200, f"{f} Hz", color='cyan', fontsize=10)

ax.set_title("EchoNet Spectrogram (Real-time)", color='white')
ax.set_ylabel("Frequency (Hz)", color='white')
ax.set_xlabel("Time (frames)", color='white')
ax.tick_params(colors='white')

try:
    stream = sd.InputStream(samplerate=FS, channels=1, blocksize=CHUNK_SIZE)
    stream.start()
except Exception as e:
    print(f"Failed to open audio stream: {e}")
    sys.exit(1)

def update(frame):
    global history
    available = stream.read_available
    if available >= CHUNK_SIZE:
        data, overflow = stream.read(CHUNK_SIZE)
        window = np.hamming(len(data))
        yf = np.abs(rfft(data.flatten() * window))
        
        # Scale magnitude to a viewable range
        yf_plot = yf[valid_idx]
        yf_db = 20 * np.log10(yf_plot + 1e-6)
        
        # Normalize arbitrarily for inferno colormap (approx 0-80 dB)
        yf_scaled = np.clip(yf_db, 0, 80) / 80.0
        
        history = np.roll(history, -1, axis=0)
        history[-1, :] = yf_scaled
        
        im.set_array(history.T)
    return [im]

ani = FuncAnimation(fig, update, interval=int(CHUNK_SIZE*1000/FS), blit=True, cache_frame_data=False)

try:
    plt.show()
except KeyboardInterrupt:
    pass
finally:
    stream.stop()
    stream.close()
    print("Visualizer stopped.")
