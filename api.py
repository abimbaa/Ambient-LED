# api.py
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from relay import write_led, connect_led, disconnect_led

app = FastAPI()
ble_lock = asyncio.Lock()  # Ensure BLE writes are sequential

class LEDCommand(BaseModel):
    r: int
    g: int
    b: int
    a: int = 0
    name: str = "ELK-BLEDDM"  # Optional, dynamic device name

@app.on_event("startup")
async def startup_event():
    """
    Connect to BLE device at startup
    """
    async with ble_lock:
        connected = await connect_led()
        if not connected:
            print("[API] BLE device not found at startup")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Disconnect BLE client safely
    """
    async with ble_lock:
        await disconnect_led()

@app.post("/led")
async def set_led(cmd: LEDCommand):
    """
    Send LED command over BLE.
    If device is disconnected, auto-connects.
    """
    async with ble_lock:
        try:
            await write_led(cmd.r, cmd.g, cmd.b, cmd.a, name=cmd.name)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"BLE write failed: {e}")
    return {"status": "sent", "cmd": f"{cmd.r},{cmd.g},{cmd.b},{cmd.a}", "device": cmd.name}

@app.get("/status")
async def status():
    """
    Return current BLE client status
    """
    from relay import client
    if client and client.is_connected:
        return {"connected": True}
    return {"connected": False}