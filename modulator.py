import numpy as np
import sounddevice as sd
import sys

# --- SAFE AUDIBLE CONFIGURATION ---
FS = 44100
BIT_DURATION = 0.2 
FREQ_START = 1000 # 1kHz (Low whistle)
FREQ_0 = 1500 
FREQ_1 = 2000 
FREQ_GAP = 2500 

def text_to_packet(text):
    bits = []
    length_bin = bin(len(text))[2:].zfill(8)
    bits.extend([int(b) for b in length_bin])
    checksum = 0
    for char in text:
        val = ord(char)
        checksum ^= val 
        bin_val = bin(val)[2:].zfill(8)
        bits.extend([int(b) for b in bin_val])
    chk_bin = bin(checksum)[2:].zfill(8)
    bits.extend([int(b) for b in chk_bin])
    return bits

def generate_tone(frequency, duration, volume=0.5): # Lower volume by default
    t = np.linspace(0, duration, int(FS * duration), endpoint=False)
    window = np.hanning(len(t))
    return volume * np.sin(2 * np.pi * frequency * t) * window

def transmit(text):
    print(f"📡 Transmitting (SAFE MODE): '{text}'")
    bits = text_to_packet(text)
    
    signal = [generate_tone(FREQ_START, 1.0)] 
    signal.append(generate_tone(FREQ_GAP, 0.1))
    
    for bit in bits:
        freq = FREQ_1 if bit == 1 else FREQ_0
        signal.append(generate_tone(freq, BIT_DURATION))
        signal.append(generate_tone(FREQ_GAP, 0.05))
    
    signal.append(generate_tone(FREQ_START, 0.5)) 
    
    full_signal = np.concatenate(signal)
    sd.play(full_signal, FS)
    sd.wait()
    print("✅ Done.")

if __name__ == "__main__":
    msg = "HELLO WORLD" if len(sys.argv) < 2 else " ".join(sys.argv[1:])
    transmit(msg)
