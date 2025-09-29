# Ambient LED System

![Status](https://img.shields.io/badge/status-frozen-lightgrey)  

**This project is currently frozen. Contributions, suggestions, and improvements are welcome!**

This project transforms a cheap Bluetooth LED strip into an ambient lighting system for your desktop.

---

## Project Overview

- **Done:**  
  - Ambient video  
- **Planned:**  
  - Ambient audio  
  - Tray application  

---

## Ambient Video

`ambient_video` is finished. It captures the mean color of your primary monitor and sends RGB values to your LED strip in real time.

### Usage

Run the `.exe` file directly on Windows, or use `relay.py` for custom scripts:

```python
from relay import connect_led, write_led, disconnect_led

# Connect to LED strip (default name is 'ELK-BLEDDM')
connect_led(name="ELK-BLEDDM")

# Send a color update (red=255, green=100, blue=50, brightness=1.0)
write_led(255, 100, 50, brightness=1.0)

# Disconnect from the LED strip
disconnect_led()
```

---

- **Notes:**
  - Default LED name is "ELK-BLEDDM".
  - Other cheap LED strips may work but are untested.
    
# IMPORTANT!
  - Make sure your LED strip is disconnected from everything like mobile apps or other devices. Most of the cheap bluetooth strips dont allow
    for more than one connection.
  - Pair with the strip in windows bluetooth settings.
---

## API server
`api.py` provides an optional live HTTP server for sending commands via POST requests (unused in ambient_video but may be useful)

```bash
uvicorn led_api:app --host 0.0.0.0 --port 8000

curl -X POST "http://127.0.0.1:8000/led"
      -H "Content-Type: application/json"
      -d "{\"r\":255,\"g\":0,\"b\":0}"
```

the server will forward these RGB values to your LED strip.

---

## Ambient audio
  - The idea was to create a script that takes desktop audio and converts it into rgb colors based on intensity and follow the beat. Calmer songs
    should display blue-purplish gradients while more energetic songs display orange-redish gradients.
  - However, I couldnt find how to do it. All the methods I tried (sounddevice and pyaudio) crashed due to conlflicts with bleak or windows.
  - Didnt want to bother with virtual audio cables aswell.
  - Any suggestion or contribution is absolutely welcome!

## Tray app
  - A simple tray app that connects all the scripts in one easy-to-use lightweight app.
  - Not started

# Contributing
  - Any contributions are welcome.
  - BLE improvements, cross-platform support, support for other LED models, and AMBIENT AUDIO or tray app is especcially welcome.
  - 
