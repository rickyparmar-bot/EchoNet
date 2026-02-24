import numpy as np
import sounddevice as sd

# --- HAMMING (7,4) ENCODER ---
def encode_hamming(bits):
    """Encodes 4 data bits into 7 bits (Hamming 7,4)."""
    d1, d2, d3, d4 = bits
    p1 = d1 ^ d2 ^ d4
    p2 = d1 ^ d3 ^ d4
    p3 = d2 ^ d3 ^ d4
    return [p1, p2, d1, p3, d2, d3, d4]

# --- CONFIGURATION ---
FS = 44100        
BIT_DURATION = 0.4 
FREQ_START = 8000 
FREQ_0 = 10000    
FREQ_1 = 12000    
FREQ_GAP = 14000 

def text_to_encoded_bits(text):
    full_bits = []
    for char in text:
        # Get 8 bits for the character
        b = bin(ord(char))[2:].zfill(8)
        b_list = [int(x) for x in b]
        # Split into two 4-bit nibbles and encode each
        full_bits.extend(encode_hamming(b_list[:4]))
        full_bits.extend(encode_hamming(b_list[4:]))
    return full_bits

def generate_tone(frequency, duration, volume=0.6):
    t = np.linspace(0, duration, int(FS * duration), endpoint=False)
    window = np.hanning(len(t))
    return volume * np.sin(2 * np.pi * frequency * t) * window

def transmit(text):
    print(f"📡 EchoNet Robust Transmitting: '{text}'")
    print("🛠️ Encoding with Hamming(7,4) Error Correction...")
    bits = text_to_encoded_bits(text)
    
    signal = [generate_tone(FREQ_START, 1.0)] # Start signal
    
    for bit in bits:
        freq = FREQ_1 if bit == 1 else FREQ_0
        signal.append(generate_tone(freq, BIT_DURATION))
        signal.append(generate_tone(FREQ_GAP, 0.1)) # Anti-echo gap
    
    signal.append(generate_tone(FREQ_START, 0.5)) # End signal
    
    full_signal = np.concatenate(signal)
    sd.play(full_signal, FS)
    sd.wait()
    print(f"✅ Sent {len(bits)} bits.")

if __name__ == "__main__":
    import sys
    msg = "MIT" if len(sys.argv) < 2 else " ".join(sys.argv[1:])
    transmit(msg)
