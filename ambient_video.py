import asyncio
import mss
from PIL import Image
import numpy as np
from relay import connect_led, write_led, disconnect_led

UPDATE_INTERVAL = 50 / 1000

def getColor():
    with mss.mss() as sct:
        screenshot = sct.grab(sct.monitors[1])
        img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)

        arr = np.array(img)
        avg_color = arr.mean(axis=(0, 1))
        return avg_color

async def main():
    await connect_led()
    try:
        while True:
            await asyncio.sleep(UPDATE_INTERVAL)
            r, g, b = getColor()
            await write_led(r, g, b)
    except asyncio.CancelledError:
        pass
    finally:
        await disconnect_led()

asyncio.run(main())