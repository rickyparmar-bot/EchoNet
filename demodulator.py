import numpy as np
import sounddevice as sd
from scipy.fft import rfft, rfftfreq
import time
import sys

# --- HIGH FREQUENCY CONFIGURATION ---
FS = 44100
FREQ_START = 8000
FREQ_0 = 10000
FREQ_1 = 12000
FREQ_GAP = 14000
CHUNK_SIZE = int(FS * 0.05) 
BIT_DURATION = 0.2

def hamming_decode_chunk(chunk):
    p1, p2, d1, p3, d2, d3, d4 = chunk
    c1 = (p1 + d1 + d2 + d4) % 2
    c2 = (p2 + d1 + d3 + d4) % 2
    c3 = (p3 + d2 + d3 + d4) % 2
    syndrome = c3 * 4 + c2 * 2 + c1
    
    if syndrome != 0:
        idx = syndrome - 1
        chunk[idx] ^= 1 # Correct single-bit error
        
    return [chunk[2], chunk[4], chunk[5], chunk[6]]

def hamming_decode_stream(stream):
    decoded = []
    for i in range(0, len(stream), 7):
        chunk = stream[i:i+7]
        if len(chunk) == 7:
            decoded.extend(hamming_decode_chunk(chunk))
    return decoded

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

def update_progress(bits, expected):
    progress = len(bits) / expected if expected != 9999 else 0
    bar = "=" * int(progress * 20)
    sys.stdout.write(f"\r[{bar:20}] Bit {len(bits)}")
    sys.stdout.flush()

def main_loop():
    print("\n🌿 EchoNet High-Freq v4.1 (Hamming FEC)")
    print("Calibrating frequencies... please wait.")
    
    # New calibration: Record 2 seconds and find noise floors for each target
    rec = sd.rec(int(FS * 1.5), samplerate=FS, channels=1)
    sd.wait()
    data = rec.flatten()
    
    mags = get_target_magnitudes(data)
    # Base noise floor on max observed + safety margin
    noise_floor = max(5.0, mags["START"] * 2.0)
    
    # We'll use a relative approach for Zero/One/Gap detection
    print(f"✅ Ready! (Base Noise Floor: {noise_floor:.2f})")
    
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
                    print("🎯 LOCK! Reading packet...", flush=True)
                    state = "DATA"
                    bits = []
                    expected_total_bits = 9999
                    last_signal_time = time.time()
                    # Reduced sleep to avoid missing data
                    sd.sleep(200)
                    continue

            elif state == "DATA":
                if time.time() - last_signal_time > 5.0:
                    print("\n⚠️ Interrupted. Resetting...", flush=True)
                    state = "IDLE"
                    continue

                # Detection logic: Gap should be clear relative to data
                is_gap = mags["GAP"] > noise_floor and mags["GAP"] > max(mags["ZERO"], mags["ONE"]) * 0.8
                
                if is_gap:
                    if last_bit != -1:
                        # print(" [GAP] ", end="", flush=True)
                        last_bit = -1
                    continue

                # Data bit detection - lowered threshold for high-freq robustness
                if mags["ONE"] > noise_floor * 0.8 and mags["ONE"] > mags["ZERO"] * 1.05:
                    if last_bit != 1:
                        bits.append(1)
                        last_bit = 1
                        last_signal_time = time.time()
                        update_progress(bits, expected_total_bits)
                
                elif mags["ZERO"] > noise_floor * 0.8 and mags["ZERO"] > mags["ONE"] * 1.05:
                    if last_bit != 0:
                        bits.append(0)
                        last_bit = 0
                        last_signal_time = time.time()
                        update_progress(bits, expected_total_bits)
                
                if expected_total_bits == 9999 and len(bits) >= 14:
                    decoded_len_bits = hamming_decode_stream(bits[:14])
                    byte = "".join(map(str, decoded_len_bits[:8]))
                    length = int(byte, 2)
                    total_decoded_bits = 8 + (length * 8) + 8
                    expected_total_bits = int(np.ceil(total_decoded_bits / 4) * 7)
                    print(f" (Incoming: {length} chars, total bits: {expected_total_bits})")

                if expected_total_bits and expected_total_bits != 9999 and len(bits) >= expected_total_bits:
                    print(f"\n🏁 ALL BITS RECEIVED.")
                    decoded_bits = hamming_decode_stream(bits[:expected_total_bits])
                    payload_bits = decoded_bits[8:len(decoded_bits)-8]
                    checksum_bits = decoded_bits[len(decoded_bits)-8:len(decoded_bits)]
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
