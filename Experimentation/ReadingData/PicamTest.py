from picamera2 import Picamera2, Preview
import time

# Create Picamera2 object
picam2 = Picamera2()

# Configure the preview
picam2.configure(picam2.preview_configuration())

# Start the preview window using DRM (fullscreen overlay on Raspberry Pi OS)
picam2.start_preview(Preview.QTGL)  # Use QTGL for a windowed preview (X11) or Preview.DRM for full screen

# Start the camera
picam2.start()

# Keep it running until interrupted
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopping preview...")

# Stop the preview and camera
picam2.stop_preview()
picam2.stop()