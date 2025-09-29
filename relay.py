# relay.py
import asyncio
import signal
from bleak import BleakClient, BleakScanner, BleakError

# ---------------- CONFIG ----------------
NAME = "ELK-BLEDDM"
MAX_CONNECT_TRIES = 5
RETRY_DELAY = 1.0  # seconds

# ---------------- GLOBALS ----------------
client: BleakClient | None = None
WRITE_UUID: str | None = None
NOTIFY_UUID: str | None = None
stop_flag = False

# ---------------- HELPERS ----------------
def handle_notify(sender, data: bytearray):
    print(f"[BLE] Notify from {sender}: {data.hex()}")

def handle_sigint(sig, frame):
    global stop_flag
    stop_flag = True

def makeCMD(r=255, g=255, b=255, a=255) -> bytes:
    return bytes([0x7E, 0x00, 0x05, 0x03, r, g, b, a, 0xEF])

# ---------------- BLE FUNCTIONS ----------------
async def connect_led(name: str = NAME) -> bool:
    """
    Connect to BLE device dynamically by name.
    Subscribes to notify characteristic automatically.
    Returns True if connected and notify subscribed.
    """
    global client, WRITE_UUID, NOTIFY_UUID

    for attempt in range(1, MAX_CONNECT_TRIES + 1):
        print(f"[BLE] Scanning for {name} (attempt {attempt})...")
        device = await BleakScanner.find_device_by_name(name)
        if device:
            break
        await asyncio.sleep(RETRY_DELAY)
    else:
        print("[BLE] Device not found")
        return False

    try:
        client = BleakClient(device, timeout=30, use_cached=False)
        await client.connect()
        print(f"[BLE] Connected to {name} at {device.address}")

        # Discover services
        for service in client.services:
            for char in service.characteristics:
                if 'notify' in char.properties and len(char.properties) == 1:
                    NOTIFY_UUID = char.uuid
                if 'write-without-response' in char.properties:
                    WRITE_UUID = char.uuid
        await asyncio.sleep(1)

        # Subscribe to notify with retries
        for _ in range(MAX_CONNECT_TRIES * 2):
            try:
                await client.start_notify(NOTIFY_UUID, handle_notify)
                print("[BLE] Notify subscription successful")
                return True
            except (BleakError, Exception) as e:
                print(f"[BLE] Notify failed: {e}, retrying...")
                if client.is_connected:
                    await client.disconnect()
                await asyncio.sleep(RETRY_DELAY)
                await client.connect()

        print("[BLE] Failed to subscribe to notify after retries")
        await client.disconnect()
        client = None
        return False

    except Exception as e:
        print(f"[BLE] Connection error: {e}")
        if client and client.is_connected:
            await client.disconnect()
        client = None
        return False

async def write_led(r=255, g=255, b=255, a=0, name: str = NAME):
    """
    Write color command to BLE device.
    Will auto-connect if not connected.
    """
    global client, WRITE_UUID
    if not client or not client.is_connected:
        success = await connect_led(name)
        if not success:
            print("[BLE] Cannot write, device not connected")
            return

    try:
        await client.write_gatt_char(WRITE_UUID, makeCMD(r, g, b, a), response=False)
        print(f"[BLE] Command sent: {r},{g},{b},{a}")
    except Exception as e:
        print(f"[BLE] Write failed: {e}")
        if client:
            await client.disconnect()
            client = None

async def disconnect_led():
    """
    Disconnect BLE client safely
    """
    global client, NOTIFY_UUID
    if client and client.is_connected:
        try:
            if NOTIFY_UUID:
                await client.stop_notify(NOTIFY_UUID)
        except Exception:
            pass
        await client.disconnect()
        client = None
        print("[BLE] Disconnected")
