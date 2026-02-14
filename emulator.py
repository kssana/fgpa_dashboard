import asyncio
import requests
import random
import numpy as np
from datetime import datetime

URL = "http://127.0.0.1:8000/ingest"

sequence_number = 0
flow_base = 500
pressure_base = 1500
vibration_freq = 5

LOW_THRESHOLD = 10
HIGH_THRESHOLD = 50

window = []


def compute_mad(signal):
    mean_val = np.mean(signal)
    return np.mean(np.abs(signal - mean_val))


async def run_emulator():
    global sequence_number
    t = 0

    while True:
        sequence_number += 1
        t += 0.5

        # --- Flow ---
        flow = flow_base + random.uniform(-5, 5)

        # Inject fault after 20 seconds
        if t > 20:
            flow += 200

        # --- Pressure ---
        pressure = pressure_base + random.uniform(-10, 10)
        if t > 20:
            pressure -= 300

        # --- Vibration ---
        vibration = 100 + 30 * np.sin(2 * np.pi * vibration_freq * t)

        # --- MAD Calculation ---
        window.append(flow)
        if len(window) > 20:
            window.pop(0)

        mad = compute_mad(window)

        # --- Compression Decision ---
        if mad < LOW_THRESHOLD:
            compression_mode = "LOSSLESS"
        elif mad < HIGH_THRESHOLD:
            compression_mode = "LOSSY"
        else:
            compression_mode = "RAW"

        # --- Build Packet ---
        data = {
            "timestamp": str(datetime.utcnow()),
            "sequence_number": sequence_number,
            "sensor_values": {
                "flow": int(flow * 10),
                "pressure": int(pressure * 20),
                "vibration": int(vibration * 10)
            },
            "compression_mode": compression_mode,
            "quantization_level": 4,
            "compression_ratio": round(random.uniform(1.5, 3.5), 2),
            "latency": round(random.uniform(5, 30), 2),
            "encryption_mode": "AES-128 (Simulated)",
            "packet_status": "OK"
        }

        try:
            requests.post(URL, json=data)
            print(f"Sent packet {sequence_number} | Mode: {compression_mode}")
        except:
            print("Server not running")

        await asyncio.sleep(0.5)


if __name__ == "__main__":
    asyncio.run(run_emulator())
