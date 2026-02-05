import cv2
import mediapipe as mp
import time
import math
import numpy as np
import pyautogui
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Initialize MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Audio setup
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

min_hand_dist = 30
max_hand_dist = 220

# Capture setup
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

vol_bar = 400
vol_per = 0
p_time = 0
mute_state = False
last_action_time = 0
lock_active = False  # 🔒 whether functions are locked

def is_hand_closed(lm_list):
    """Return True if hand is closed (fist)."""
    if not lm_list or len(lm_list) < 21:
        return False
    # Compare fingertip y with corresponding MCP y positions
    finger_tips = [8, 12, 16, 20]
    finger_mcps = [5, 9, 13, 17]
    return all(lm_list[tip][2] > lm_list[mcp][2] for tip, mcp in zip(finger_tips, finger_mcps))

def is_hand_open(lm_list):
    """Return True if hand is open."""
    if not lm_list or len(lm_list) < 21:
        return False
    finger_tips = [8, 12, 16, 20]
    finger_mcps = [5, 9, 13, 17]
    return all(lm_list[tip][2] < lm_list[mcp][2] for tip, mcp in zip(finger_tips, finger_mcps))

while True:
    success, img = cap.read()
    if not success:
        break

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    lm_sets = []
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            lm_list = []
            h, w, _ = img.shape
            for id, lm in enumerate(hand_landmarks.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append([id, cx, cy])
            lm_sets.append(lm_list)
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Determine which hand is lock vs control
    if len(lm_sets) == 2:
        # Decide lock hand (leftmost one)
        lock_hand = lm_sets[0] if lm_sets[0][0][1] < lm_sets[1][0][1] else lm_sets[1]
        control_hand = lm_sets[1] if lock_hand == lm_sets[0] else lm_sets[0]
    elif len(lm_sets) == 1:
        # Only one hand → control hand active, lock hand not present
        control_hand = lm_sets[0]
        lock_hand = None
    else:
        control_hand = lock_hand = None

    # 🔒 Check lock/unlock
    if lock_hand:
        if is_hand_closed(lock_hand):
            lock_active = True
            cv2.putText(img, "LOCKED", (950, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 4)
        elif is_hand_open(lock_hand):
            lock_active = False
            cv2.putText(img, "UNLOCKED", (950, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 4)

    # If locked, skip all controls
    if lock_active:
        cv2.putText(img, "Controls Disabled", (500, 700), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        cv2.imshow("Hand Control", img)
        if cv2.waitKey(1) & 0xFF == 27:
            break
        continue

    # --- Control hand gestures ---
    if control_hand:
        # Volume control
        x1, y1 = control_hand[4][1], control_hand[4][2]   # Thumb tip
        x2, y2 = control_hand[8][1], control_hand[8][2]   # Index tip
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)

        length = math.hypot(x2 - x1, y2 - y1)
        vol_per = np.interp(length, [min_hand_dist, max_hand_dist], [0, 100])
        vol_bar = np.interp(length, [min_hand_dist, max_hand_dist], [400, 150])
        volume.SetMasterVolumeLevelScalar(vol_per / 100, None)

        if length < min_hand_dist + 10:
            cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)

        # Mute/Unmute
        pinky_tip, pinky_mcp = control_hand[20][2], control_hand[17][2]
        if pinky_tip < pinky_mcp and not mute_state:
            volume.SetMute(1, None)
            mute_state = True
            print("Muted")
        elif pinky_tip >= pinky_mcp and mute_state:
            volume.SetMute(0, None)
            mute_state = False
            print("Unmuted")

        current_time = time.time()

        # Play / Pause
        middle_tip, middle_mcp = control_hand[12][2], control_hand[9][2]
        ring_tip, ring_mcp = control_hand[16][2], control_hand[13][2]
        if middle_tip < middle_mcp and current_time - last_action_time > 1:
            pyautogui.press("playpause")
            last_action_time = current_time
            print("Play triggered")

        if ring_tip < ring_mcp and current_time - last_action_time > 1:
            pyautogui.press("playpause")
            last_action_time = current_time
            print("Pause triggered")

    # UI Elements
    cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
    cv2.rectangle(img, (50, int(vol_bar)), (85, 400), (255, 0, 0), cv2.FILLED)
    cv2.putText(img, f"{int(vol_per)} %", (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

    c_time = time.time()
    fps = 1 / (c_time - p_time) if c_time != p_time else 0
    p_time = c_time
    cv2.putText(img, f'FPS: {int(fps)}', (20, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 2)

    cv2.imshow("Hand Control", img)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
