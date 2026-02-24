import numpy as np
import soundfile as sf
from modulator import text_to_encoded_bits, generate_tone, FREQ_START, FREQ_0, FREQ_1, FREQ_GAP, BIT_DURATION
from demodulator import decode_hamming, get_peak

def run_simulation(message):
    print(f"🧪 Starting EchoNet Simulation for: '{message}'")
    fs = 44100
    
    # 1. ENCODE (Transmitter Logic)
    print("🛰️  Encoding bits...")
    bits = text_to_encoded_bits(message)
    signal = [generate_tone(FREQ_START, 1.0)]
    for bit in bits:
        freq = FREQ_1 if bit == 1 else FREQ_0
        signal.append(generate_tone(freq, BIT_DURATION))
        signal.append(generate_tone(FREQ_GAP, 0.1))
    signal.append(generate_tone(FREQ_START, 0.5))
    
    full_signal = np.concatenate(signal)
    
    # 2. ADD NOISE (Simulating the real world)
    print("🌪️  Adding 10% white noise to simulate room environment...")
    noise = np.random.normal(0, 0.05, full_signal.shape)
    full_signal = full_signal + noise
    
    # 3. DECODE (Receiver Logic)
    print("👂 Decoding from virtual buffer...")
    decoded_bits = []
    chunk_size = int(fs * 0.05)
    
    ptr = int(fs * 1.1) # Skip start chirp
    last_bit = -1
    
    while ptr < len(full_signal) - chunk_size:
        chunk = full_signal[ptr : ptr + chunk_size]
        peak, mag = get_peak(chunk)
        
        if abs(peak - 14000) < 500: # FREQ_GAP
            last_bit = -1
        elif abs(peak - 12000) < 500: # FREQ_1
            if last_bit != 1:
                decoded_bits.append(1)
                last_bit = 1
        elif abs(peak - 10000) < 500: # FREQ_0
            if last_bit != 0:
                decoded_bits.append(0)
                last_bit = 0
        elif abs(peak - 8000) < 400 and len(decoded_bits) >= 14:
            break
            
        ptr += chunk_size

    # 4. ERROR CORRECTION (Hamming)
    print(f"✅ Captured {len(decoded_bits)} bits. Applying Hamming correction...")
    data_bits = []
    for i in range(0, (len(decoded_bits)//7)*7, 7):
        block = decoded_bits[i:i+7]
        data_bits.extend(decode_hamming(block))
    
    final_msg = ""
    for i in range(0, (len(data_bits)//8)*8, 8):
        byte = "".join(map(str, data_bits[i:i+8]))
        final_msg += chr(int(byte, 2))
        
    print(f"\n🎉 SIMULATION RESULT: '{final_msg}'")
    if final_msg == message:
        print("🏆 PROTOCOL VERIFIED: 100% Accuracy with noise.")
    else:
        print(f"❌ PROTOCOL ERROR: Expected '{message}', but got '{final_msg}'")

if __name__ == "__main__":
    run_simulation("MIT 2026")
