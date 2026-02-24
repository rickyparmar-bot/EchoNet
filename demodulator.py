import numpy as np
import sounddevice as sd
from scipy.fft import rfft, rfftfreq
import time
import sys

# --- SAFE AUDIBLE CONFIGURATION ---
FS = 44100
FREQ_START = 1000
FREQ_0 = 1500
FREQ_1 = 2000
FREQ_GAP = 2500
CHUNK_SIZE = int(FS * 0.05) 
BIT_DURATION = 0.2

def get_target_magnitudes(data):
    window = np.hamming(len(data))
    yf = rfft(data * window)
    xf = rfftfreq(len(data), 1/FS)
    def mag_at(freq):
        idx = np.where((xf > freq - 100) & (xf < freq + 100))[0]
        return np.max(np.abs(yf[idx])) if len(idx) > 0 else 0
    return {
        "START": mag_at(FREQ_START),
        "ZERO": mag_at(FREQ_0),
        "ONE": mag_at(FREQ_1),
        "GAP": mag_at(FREQ_GAP)
    }

def main_loop():
    print("\n🌿 EchoNet Safe Mode v3.5 (Audible)")
    print("Calibrating... stay quiet.")
    
    calibration_data = []
    for _ in range(10):
        rec = sd.rec(int(FS * 0.1), samplerate=FS, channels=1)
        sd.wait()
        calibration_data.append(get_target_magnitudes(rec.flatten())["START"])
    
    noise_floor = np.max(calibration_data) * 3.0
    print(f"✅ Ready! (Noise Floor: {noise_floor:.2f})")
    
    state = "IDLE" 
    bits = []
    expected_total_bits = None
    last_signal_time = time.time()
    last_bit = -1

    while True:
        try:
            rec = sd.rec(CHUNK_SIZE, samplerate=FS, channels=1)
            sd.wait()
            mags = get_target_magnitudes(rec.flatten())

            if state == "IDLE":
                if mags["START"] > noise_floor and mags["START"] > 5.0:
                    print("🎯 LOCK! Reading packet...")
                    state = "DATA"
                    bits = []
                    expected_total_bits = 9999
                    last_signal_time = time.time()
                    sd.sleep(1000)
                    continue

            elif state == "DATA":
                if time.time() - last_signal_time > 5.0:
                    print("\n⚠️ Interrupted. Resetting...")
                    state = "IDLE"
                    continue

                if mags["GAP"] > noise_floor and mags["GAP"] > max(mags["ZERO"], mags["ONE"]):
                    last_bit = -1
                    continue

                if mags["ONE"] > noise_floor and mags["ONE"] > mags["ZERO"] * 1.2:
                    if last_bit != 1:
                        bits.append(1)
                        last_bit = 1
                        last_signal_time = time.time()
                        progress = len(bits) / expected_total_bits if expected_total_bits != 9999 else 0
                        bar = "=" * int(progress * 20)
                        sys.stdout.write(f"\r[{bar:20}] Bit {len(bits)}")
                        sys.stdout.flush()
                
                elif mags["ZERO"] > noise_floor and mags["ZERO"] > mags["ONE"] * 1.2:
                    if last_bit != 0:
                        bits.append(0)
                        last_bit = 0
                        last_signal_time = time.time()
                        progress = len(bits) / expected_total_bits if expected_total_bits != 9999 else 0
                        bar = "=" * int(progress * 20)
                        sys.stdout.write(f"\r[{bar:20}] Bit {len(bits)}")
                        sys.stdout.flush()
                
                if expected_total_bits == 9999 and len(bits) >= 8:
                    byte = "".join(map(str, bits[:8]))
                    length = int(byte, 2)
                    expected_total_bits = 8 + (length * 8) + 8
                    print(f" (Incoming: {length} chars)")

                if expected_total_bits and len(bits) >= expected_total_bits:
                    print(f"\n🏁 ALL BITS RECEIVED.")
                    payload_bits = bits[8:expected_total_bits-8]
                    checksum_bits = bits[expected_total_bits-8:expected_total_bits]
                    chars = []
                    calc_sum = 0
                    for i in range(0, len(payload_bits), 8):
                        byte_str = "".join(map(str, payload_bits[i:i+8]))
                        if len(byte_str) == 8:
                            val = int(byte_str, 2)
                            chars.append(chr(val))
                            calc_sum ^= val
                    got_sum = int("".join(map(str, checksum_bits)), 2)
                    print("---------------------------------------")
                    print(f"📩 MESSAGE: {''.join(chars)}")
                    print(f"🔒 STATUS:  {'VALID' if calc_sum == got_sum else 'CORRUPTED'}")
                    print("---------------------------------------\n")
                    state = "IDLE"
                    bits = []
                    expected_total_bits = None
                    last_bit = -1

        except KeyboardInterrupt:
            sys.exit(0)

if __name__ == "__main__":
    main_loop()
