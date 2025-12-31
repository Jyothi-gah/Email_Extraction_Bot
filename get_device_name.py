import subprocess

def list_dshow_devices():
    cmd = ['ffmpeg', '-list_devices', 'true', '-f', 'dshow', '-i', 'dummy']
    process = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    stdout, stderr = process.communicate()
    
    # FFmpeg writes device info to stderr, not stdout
    output = stderr.decode('utf-8', errors='ignore')
    print("=== AVAILABLE AUDIO DEVICES ===")
    print(output)
    print("===============================")
    print("\nLOOK FOR lines starting with [dshow]. Find the one related to 'CABLE Output'.")
    print("Example: 'CABLE Output (VB-Audio Virtual Cable)'")

if __name__ == "__main__":
    list_dshow_devices()