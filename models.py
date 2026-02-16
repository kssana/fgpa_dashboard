from pydantic import BaseModel
from typing import Dict

class Telemetry(BaseModel):
    timestamp: str
    sequence_number: int
    sensor_values: Dict[str, int]
    compression_mode: str
    quantization_level: int
    compression_ratio: float
    latency: float
    encryption_mode: str
    packet_status: str

