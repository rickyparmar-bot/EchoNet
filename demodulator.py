import numpy as np
import sounddevice as sd
from scipy.fft import rfft, rfftfreq

# --- HAMMING (7,4) DECODER ---
def decode_hamming(bits):
    """Decodes 7 bits into 4 data bits, correcting single errors."""
    p1, p2, d1, p3, d2, d3, d4 = bits
    s1 = p1 ^ d1 ^ d2 ^ d4
    s2 = p2 ^ d1 ^ d3 ^ d4
    s3 = p3 ^ d2 ^ d3 ^ d4
    
    error_pos = s1 + (s2 * 2) + (s3 * 4)
    if error_pos != 0:
        print(f"🛠️  Correcting error at bit {error_pos}...")
        # Map Hamming position to index
        idx_map = [None, 0, 1, 2, 3, 4, 5, 6] # pos -> bits index
        bits[error_pos-1] ^= 1 # Flip the bit
        
    return [bits[2], bits[4], bits[5], bits[6]]

# --- CONFIGURATION ---
FS = 44100
FREQ_START = 8000
FREQ_0 = 10000
FREQ_1 = 12000
FREQ_GAP = 14000
CHUNK_SIZE = int(FS * 0.05) 

def get_peak(data):
    yf = rfft(data * np.hamming(len(data)))
    xf = rfftfreq(len(data), 1/FS)
    idx = np.argmax(np.abs(yf))
    return xf[idx], np.abs(yf[idx])

def listen():
    print("👂 EchoNet Robust: Waiting for encoded signal...")
    bits = []
    state = "IDLE" 
    last_bit = -1

    while True:
        rec = sd.rec(CHUNK_SIZE, samplerate=FS, channels=1)
        sd.wait()
        peak, mag = get_peak(rec.flatten())

        if mag < 2.0: continue

        if state == "IDLE":
            if abs(peak - FREQ_START) < 400:
                print("🎯 START detected! Receiving ECC blocks...")
                state = "DATA"
                sd.sleep(1000)

        elif state == "DATA":
            if abs(peak - FREQ_GAP) < 500:
                last_bit = -1
                continue

            if abs(peak - FREQ_1) < 500:
                if last_bit != 1:
                    bits.append(1)
                    print("1", end="", flush=True)
                    last_bit = 1
            elif abs(peak - FREQ_0) < 500:
                if last_bit != 0:
                    bits.append(0)
                    print("0", end="", flush=True)
                    last_bit = 0
            elif abs(peak - FREQ_START) < 400 and len(bits) >= 7:
                print("\n🏁 END detected.")
                break

    if len(bits) < 14:
        print(f"\n❌ Signal too short ({len(bits)} bits). Need at least 14 for one character.")
        return

    print(f"\n✅ Captured {len(bits)} raw bits.")
    
    # Process 7-bit Hamming blocks
    data_bits = []
    for i in range(0, (len(bits)//7)*7, 7):
        block = bits[i:i+7]
        data_bits.extend(decode_hamming(block))
    
    # Convert 4-bit nibbles back to 8-bit characters
    msg = ""
    for i in range(0, (len(data_bits)//8)*8, 8):
        byte = "".join(map(str, data_bits[i:i+8]))
        msg += chr(int(byte, 2))
    
    print(f"📩 Final Corrected Message: {msg}")

if __name__ == "__main__":
    try: listen()
    except KeyboardInterrupt: pass
