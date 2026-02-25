import numpy as np
import sounddevice as sd
import sys

# --- HIGH FREQUENCY CONFIGURATION ---
FS = 44100
BIT_DURATION = 0.2 
FREQ_START = 8000 
FREQ_0 = 10000 
FREQ_1 = 12000 
FREQ_GAP = 14000 

def hamming_encode(bits):
    encoded = []
    padded_bits = bits + [0] * ((4 - len(bits) % 4) % 4)
    for i in range(0, len(padded_bits), 4):
        d1, d2, d3, d4 = padded_bits[i:i+4]
        p1 = (d1 + d2 + d4) % 2
        p2 = (d1 + d3 + d4) % 2
        p3 = (d2 + d3 + d4) % 2
        encoded.extend([p1, p2, d1, p3, d2, d3, d4])
    return encoded

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
    print(f"📡 Transmitting (HAMMING FEC): '{text}'")
    bits = text_to_packet(text)
    
    encoded_bits = hamming_encode(bits)
    
    signal = [generate_tone(FREQ_START, 1.0)] 
    signal.append(generate_tone(FREQ_GAP, 0.1))
    
    for bit in encoded_bits:
        freq = FREQ_1 if bit == 1 else FREQ_0
        signal.append(generate_tone(freq, BIT_DURATION))
        signal.append(generate_tone(FREQ_GAP, 0.1))
    
    signal.append(generate_tone(FREQ_START, 0.5)) 
    
    full_signal = np.concatenate(signal)
    sd.play(full_signal, FS)
    sd.wait()
    print("✅ Done.")

if __name__ == "__main__":
    msg = "HELLO WORLD" if len(sys.argv) < 2 else " ".join(sys.argv[1:])
    transmit(msg)
