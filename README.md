🖐️ AI Device Volume Control using Hand Gestures

This project is a real-time hand gesture–based system volume and media controller built using OpenCV, MediaPipe, and PyCaw.
It uses a webcam to detect hand gestures and allows you to control system volume, mute/unmute, play/pause media, and lock/unlock controls without touching the keyboard or mouse.

🚀 Features

🎥 Real-time hand tracking using MediaPipe Hands

🔊 Volume control using thumb–index finger distance

🔇 Mute / Unmute using pinky finger gesture

⏯ Play / Pause media using finger gestures

🔒 Lock / Unlock system controls using second hand

📊 On-screen UI:

Volume bar

Volume percentage

FPS counter

Lock/Unlock status

🖐️ Gesture Controls
🔊 Volume Control

Move thumb and index finger closer → decrease volume

Move thumb and index finger apart → increase volume

🔇 Mute / Unmute

Pinky finger up → Mute

Pinky finger down → Unmute

⏯ Media Control

Middle finger up → Play

Ring finger up → Pause
(1-second cooldown to prevent multiple triggers)

🔒 Lock / Unlock

Use second hand (leftmost hand):

✊ Closed fist → LOCK controls

✋ Open palm → UNLOCK controls

🛠️ Requirements
💻 Operating System

Windows only (because pycaw controls Windows system volume)

🐍 Python Version

✅ Python 3.9 / 3.10 / 3.11
❌ Python 3.12+ / 3.14 is not supported by MediaPipe

📦 Required Libraries

Install all dependencies using:

pip install opencv-python mediapipe numpy pyautogui pycaw comtypes

▶️ How to Run

Clone or download the project

Open Command Prompt

Navigate to the project folder:

cd AI_DEVICE_VOLUME_CONTROL-main


Run the script:

python AI_volume_control.py


Press ESC to exit the application

⚠️ Important Notes

Ensure no file or folder is named mediapipe.py in your project directory
(this causes AttributeError: module 'mediapipe' has no attribute 'solutions')

Run the script using Python, not Java or Code Runner

Allow camera access when prompted

Ensure only one instance of the webcam is running

🧠 Technologies Used

Python

OpenCV

MediaPipe

NumPy

PyAutoGUI

PyCaw (Windows Audio Control)

📸 Output Preview

Webcam feed with hand landmarks

Volume bar on the left

FPS counter

Lock/Unlock status display
