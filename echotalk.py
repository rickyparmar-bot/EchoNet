import numpy as np
import sounddevice as sd
from scipy.fft import rfft, rfftfreq
import time
import sys
import threading

# --- CONFIGURATION ---
FS = 44100
BIT_DURATION = 0.15
FREQ_START = 1000
FREQ_0 = 1500
FREQ_1 = 2000
FREQ_GAP = 2500
CHUNK_SIZE = int(FS * 0.05)

class EchoTalk:
    def __init__(self):
        self.is_transmitting = False
        self.running = True
        self.bits = []
        self.state = "IDLE"
        self.expected_bits = 9999
        self.last_bit = -1
        self.last_signal_time = time.time()
        self.noise_floor = 5.0

    def generate_tone(self, freq, duration, vol=0.6):
        t = np.linspace(0, duration, int(FS * duration), endpoint=False)
        return vol * np.sin(2 * np.pi * freq * t) * np.hanning(len(t))

    def transmit(self, text):
        self.is_transmitting = True
        print(f"
📡 SENDING: {text}")
        
        # Build Packet
        bits = []
        length_bin = bin(len(text))[2:].zfill(8)
        bits.extend([int(b) for b in length_bin])
        checksum = 0
        for char in text:
            val = ord(char)
            checksum ^= val
            bits.extend([int(b) for b in bin(val)[2:].zfill(8)])
        bits.extend([int(b) for b in bin(checksum)[2:].zfill(8)])

        # Generate Audio
        signal = [self.generate_tone(FREQ_START, 1.0), self.generate_tone(FREQ_GAP, 0.1)]
        for bit in bits:
            freq = FREQ_1 if bit == 1 else FREQ_0
            signal.append(self.generate_tone(freq, BIT_DURATION))
            signal.append(self.generate_tone(FREQ_GAP, 0.05))
        signal.append(self.generate_tone(FREQ_START, 0.3))

        full_audio = np.concatenate(signal)
        sd.play(full_audio, FS)
        sd.wait()
        
        self.is_transmitting = False
        print("✅ SENT. Listening...
> ", end="", flush=True)

    def get_mags(self, data):
        yf = rfft(data * np.hamming(len(data)))
        xf = rfftfreq(len(data), 1/FS)
        def mag_at(f):
            idx = np.where((xf > f-100) & (xf < f+100))[0]
            return np.max(np.abs(yf[idx])) if len(idx) > 0 else 0
        return {"S": mag_at(FREQ_START), "0": mag_at(FREQ_0), "1": mag_at(FREQ_1), "G": mag_at(FREQ_GAP)}

    def listen_thread(self):
        while self.running:
            if self.is_transmitting:
                time.sleep(0.1)
                continue

            rec = sd.rec(CHUNK_SIZE, samplerate=FS, channels=1)
            sd.wait()
            mags = self.get_mags(rec.flatten())

            if self.state == "IDLE":
                if mags["S"] > self.noise_floor * 2 and mags["S"] > 10:
                    print("
🎯 INCOMING...")
                    self.state = "DATA"
                    self.bits = []
                    self.expected_bits = 9999
                    self.last_signal_time = time.time()
                    sd.sleep(1100)

            elif self.state == "DATA":
                if time.time() - self.last_signal_time > 5.0:
                    self.state = "IDLE"
                    print("
⚠️ LOST.")
                    continue

                if mags["G"] > mags["0"] and mags["G"] > mags["1"]:
                    self.last_bit = -1
                    continue

                for bit, freq in [(1, "1"), (0, "0")]:
                    if mags[freq] > 5.0 and mags[freq] > mags[str(1-bit)] * 1.2:
                        if self.last_bit != bit:
                            self.bits.append(bit)
                            self.last_bit = bit
                            self.last_signal_time = time.time()
                            sys.stdout.write("#")
                            sys.stdout.flush()

                if self.expected_bits == 9999 and len(self.bits) >= 8:
                    self.expected_bits = 8 + (int("".join(map(str, self.bits[:8])), 2) * 8) + 8

                if len(self.bits) >= self.expected_bits:
                    # Decode
                    payload = self.bits[8:-8]
                    chk_bits = self.bits[-8:]
                    msg = ""
                    calc_sum = 0
                    for i in range(0, len(payload), 8):
                        val = int("".join(map(str, payload[i:i+8])), 2)
                        msg += chr(val)
                        calc_sum ^= val
                    
                    got_sum = int("".join(map(str, chk_bits)), 2)
                    status = "✅" if calc_sum == got_sum else "❌"
                    print(f"
📩 {status} RECEIVED: {msg}
> ", end="", flush=True)
                    self.state = "IDLE"

    def run(self):
        print("🎙️ EchoTalk v1.0 - Acoustic Chat")
        print("Type a message and press Enter. Stay quiet to listen.
")
        
        t = threading.Thread(target=self.listen_thread)
        t.daemon = True
        t.start()

        try:
            while True:
                msg = input("> ")
                if msg.strip():
                    self.transmit(msg)
        except KeyboardInterrupt:
            self.running = False
            print("
Bye!")

if __name__ == "__main__":
    app = EchoTalk()
    app.run()
