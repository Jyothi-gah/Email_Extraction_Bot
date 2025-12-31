import os

# EMAIL CONFIG
EMAIL_USER = "jyothijyo0407@gmail.com"
EMAIL_PASS = "plbyyhsmfnrzvwqb"
IMAP_SERVER = "imap.gmail.com"

# AUDIO CONFIG (VB-Cable)
AUDIO_DEVICE_NAME = "CABLE Output (VB-Audio Virtual Cable)"

OUTPUT_DIR = "Recordings"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)