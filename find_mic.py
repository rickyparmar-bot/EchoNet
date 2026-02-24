import sounddevice as sd
import numpy as np

def find_mic():
    print("🔍 Searching for working input devices...")
    devices = sd.query_devices()
    input_devices = []
    
    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0:
            input_devices.append(i)
            print(f"[{i}] {dev['name']} (Channels: {dev['max_input_channels']})")

    if not input_devices:
        print("❌ No input devices found!")
        return

    for idx in input_devices:
        print(f"
🎤 Testing Device [{idx}]...")
        try:
            # Record 1 second
            duration = 1.0
            fs = 44100
            recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, device=idx)
            sd.wait()
            mag = np.max(np.abs(recording))
            print(f"   Max Amplitude: {mag:.5f}")
            if mag > 0.00001:
                print(f"   ✅ Device [{idx}] is picking up signal!")
            else:
                print(f"   ⚠️ Device [{idx}] is silent. Is it muted?")
        except Exception as e:
            print(f"   ❌ Error testing device {idx}: {e}")

if __name__ == "__main__":
    find_mic()
