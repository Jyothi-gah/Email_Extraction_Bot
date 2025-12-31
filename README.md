📧 Email Extraction & Meeting Automation Bot 


📌 Overview

The Email Extraction Bot is an automation tool that monitors emails to detect scheduled online meetings and automatically joins them. Once a meeting is detected, the bot joins instantly, records the session, and extracts key metadata for documentation purposes.
The bot supports Zoom, Google Meet, and Zoho Meeting platforms.


🚀 Key Features

📬 Email Monitoring – Detects meeting invitations directly from emails

🔗 Auto Meeting Join – Joins the meeting immediately when a valid link is found

🎥 Fake Audio & Video Stream – Uses virtual audio/video devices to simulate a real participant

🎙️ Meeting Recording – Captures meeting audio using FFmpeg and VB-Cable

📝 Metadata Extraction – Generates a structured .txt file containing:

To,
From,
CC,
Meeting platform,
Meeting link,
Date & time (if available)




🚪 Smart Exit Logic – Automatically leaves the meeting when:

Host ends the meeting , 
“No one else is here” message appears ,
Similar termination notifications are detected 


🛠️ Tech Stack

FFmpeg – Audio recording

VB-Cable – Virtual audio routing

Automation Scripts – Meeting join & monitoring logic

Virtual Camera & Mic – Fake audio/video stream



📂 Output

Text File (.txt) Contains extracted email and meeting details for record-keeping.

Audio File (.wav / .mp3) Full meeting audio recording.



🧠 Supported Platforms

Zoom

Google Meet

Zoho Meeting



⚙️ Bot Workflow

Bot scans incoming emails

Detects meeting invitation links

Instantly joins the meeting

Records audio in real time

Extracts meeting & email metadata

Automatically exits when meeting ends

Saves outputs locally


