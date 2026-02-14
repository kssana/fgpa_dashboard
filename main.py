from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from models import Telemetry

app = FastAPI()

# Allow frontend to connect later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store connected WebSocket clients
connected_clients: List[WebSocket] = []


@app.get("/")
def root():
    return {"message": "FPGA Telemetry Backend Running"}


@app.post("/ingest")
async def ingest(data: Telemetry):
    # Broadcast received telemetry to all connected WebSocket clients
    for client in connected_clients:
        await client.send_json(data.dict())

    return {"status": "Telemetry received"}


@app.websocket("/ws/telemetry")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)

    try:
        while True:
            await websocket.receive_text()  # keep connection alive
    except:
        connected_clients.remove(websocket)
