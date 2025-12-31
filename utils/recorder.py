import subprocess
import signal
import os
import time

class AudioRecorder:
    def __init__(self, filename, device_name):
        self.filename = filename
        self.device_name = device_name
        self.process = None

    def start(self):
        # Build the FFmpeg command
        # -y: Overwrite output
        # -f dshow: DirectShow (Windows)
        # -i audio="...": Input device
        cmd = [
            'ffmpeg', 
            '-y', 
            '-f', 'dshow', 
            '-i', f'audio={self.device_name}', 
            self.filename
        ]
        
        # Start recording in background without popping up a window
        print(f"Starting FFmpeg recording on device: {self.device_name}")
        self.process = subprocess.Popen(
            cmd, 
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )

    def stop(self):
        if self.process:
            print("Stopping recording...")
            # Send 'q' to ffmpeg to stop gracefully and save headers
            try:
                self.process.communicate(input=b'q', timeout=5)
            except subprocess.TimeoutExpired:
                self.process.terminate()
            
            print(f"Recording saved to {self.filename}")