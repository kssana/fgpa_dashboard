import asyncio
import requests
import random
import numpy as np
from datetime import datetime, timezone

URL = "https://fgpa-dashboard.onrender.com/ingest"

sequence_number = 0
t = 0.0

# Baselines (industrial-style)
FLOW_BASE = 500        # GPM
PRESSURE_BASE = 1500   # PSI
VIB_FREQ = 5           # Hz

LOW_MAD = 10
HIGH_MAD = 50

window = []


def compute_mad(signal):
    mean = np.mean(signal)
    return np.mean(np.abs(signal - mean))


async def run_emulator():
    global sequence_number, t

    while True:
        sequence_number += 1
        t += 0.5

        # --- Physical signals ---
        flow = FLOW_BASE + random.gauss(0, 3)
        pressure = PRESSURE_BASE + random.gauss(0, 8)
        vibration = 100 + 30 * np.sin(2 * np.pi * VIB_FREQ * t) + random.gauss(0, 5)

        # --- Fault injection (after 20s) ---
        system_state = "NORMAL"
        if t > 20:
            flow += 200
            pressure -= 300
            vibration *= 1.5
            system_state = "FAULT"

        # --- MAD-based analysis ---
        window.append(flow)
        if len(window) > 20:
            window.pop(0)

        mad = compute_mad(window)

        # --- Compression decision ---
        if mad < LOW_MAD:
            compression_mode = "LOSSLESS"
            compressed_bits = 8
        elif mad < HIGH_MAD:
            compression_mode = "LOSSY"
            compressed_bits = 4
        else:
            compression_mode = "RAW"
            compressed_bits = 16

        # --- Compression ratio (real, not random) ---
        raw_bits = 16
        compression_ratio = raw_bits / compressed_bits

        # --- Latency model (industry-style) ---
        compression_delay = {
            "RAW": 2,
            "LOSSLESS": 6,
            "LOSSY": 10
        }[compression_mode]

        encryption_delay = 5     # AES hardware equivalent
        network_jitter = random.uniform(5, 15)

        latency = compression_delay + encryption_delay + network_jitter

        # --- Build packet ---
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sequence_number": sequence_number,
            "sensor_values": {
                "flow": flow,
                "pressure": pressure,
                "vibration": vibration
            },
            "system_state": system_state,
            "compression_mode": compression_mode,
            "quantization_level": compressed_bits,
            "compression_ratio": round(compression_ratio, 2),
            "latency": round(latency, 2),
            "encryption_mode": "AES-128 (Simulated)",
            "packet_status": "OK"
        }

        try:
            requests.post(URL, json=payload, timeout=2)
            print(f"Pkt {sequence_number} | {system_state} | {compression_mode}")
        except:
            print("Backend unreachable")

        await asyncio.sleep(0.5)


if __name__ == "__main__":
    asyncio.run(run_emulator())
