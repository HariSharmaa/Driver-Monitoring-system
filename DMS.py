import cv2
import mediapipe as mp
import numpy as np
import time
import pygame

# =========================
# INITIALIZE AUDIO & MODELS
# =========================
pygame.mixer.init()
try:
    alarm_sound = pygame.mixer.Sound("assets/samsung alarm.mp3")
except:
    alarm_sound = None

mp_face_mesh = mp.solutions.face_mesh
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, refine_landmarks=True)
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.7, min_tracking_confidence=0.6)

# =========================
# CONSTANTS & THRESHOLDS
# =========================
EYE_AR_THRESH = 0.22
MOUTH_AR_THRESH = 0.40 
DROWSY_LIMIT = 2.0 
YAWN_LIMIT = 2.0 
FILTER_SIZE = 5

# =========================
# STABLE HELPER FUNCTIONS
# =========================
def get_ear(landmarks, eye_indices):
    p = [np.array([landmarks[i].x, landmarks[i].y]) for i in eye_indices]
    v1 = np.linalg.norm(p[1] - p[5])
    v2 = np.linalg.norm(p[2] - p[4])
    h = np.linalg.norm(p[0] - p[3])
    return (v1 + v2) / (2.0 * h)

def get_mar(landmarks):
    top = np.array([landmarks[13].x, landmarks[13].y])
    bottom = np.array([landmarks[14].x, landmarks[14].y])
    left = np.array([landmarks[78].x, landmarks[78].y])
    right = np.array([landmarks[308].x, landmarks[308].y])
    return np.linalg.norm(top - bottom) / np.linalg.norm(left - right)

def get_smooth_value(current_value, history_list):
    history_list.append(current_value)
    if len(history_list) > FILTER_SIZE:
        history_list.pop(0)
    return sum(history_list) / len(history_list)

def is_thumbs_up(hand_lms):
    l = hand_lms.landmark
    
    # 1. Four fingers must be curled (Tip y > PIP joint y)
    fingers_curled = all(l[tip].y > l[tip - 2].y for tip in [8, 12, 16, 20])
    
    # 2. Thumb tip must be above the thumb base and the wrist
    thumb_is_up = l[4].y < l[3].y < l[5].y
    
    # 3. Thumb tip must be the highest point of the entire hand
    thumb_topmost = all(l[4].y < l[i].y for i in range(5, 21))
    
    return fingers_curled and thumb_is_up and thumb_topmost

def trigger_alarm():
    global alarm_active, alarm_start_time
    if not alarm_active:
        alarm_active = True
        alarm_start_time = time.time()
        if alarm_sound:
            alarm_sound.play(-1) # Play on loop

# =========================
# STATE VARIABLES
# =========================
eye_closed_start = None
yawn_start = None
yawn_counter = 0
alarm_active = False
alarm_start_time = None
driver_status = "NORMAL"
show_mesh = True  # Toggle for visualization
yawn_debounce = False
thumb_confirm_start = None  # Timer for holding the gesture

ear_history = []
mar_history = []

cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, frame = cap.read()
    if not success: break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    face_res = face_mesh.process(rgb)
    hand_res = hands.process(rgb)

    # 1. FACE ANALYSIS
    if face_res.multi_face_landmarks:
        face_landmarks_obj = face_res.multi_face_landmarks[0]
        lms = face_landmarks_obj.landmark

        # Draw Face Meshes if enabled
        if show_mesh:
            mp_drawing.draw_landmarks(frame, face_landmarks_obj, mp_face_mesh.FACEMESH_TESSELATION, None, mp_drawing_styles.get_default_face_mesh_tesselation_style())
            mp_drawing.draw_landmarks(frame, face_landmarks_obj, mp_face_mesh.FACEMESH_CONTOURS, None, mp_drawing_styles.get_default_face_mesh_contours_style())

        # Math Calculations
        raw_ear = (get_ear(lms, [33,160,158,133,153,144]) + get_ear(lms, [263,387,385,362,380,373])) / 2.0
        raw_mar = get_mar(lms)
        ear = get_smooth_value(raw_ear, ear_history)
        mar = get_smooth_value(raw_mar, mar_history)

        # Logic for Sleepy (Eyes)
        if ear < EYE_AR_THRESH:
            if eye_closed_start is None: eye_closed_start = time.time()
            elif (time.time() - eye_closed_start) > DROWSY_LIMIT:
                driver_status = "SLEEPY"
                trigger_alarm()
        else:
            eye_closed_start = None
            if driver_status == "SLEEPY": driver_status = "NORMAL"

        # Logic for Yawning (Counter triggers on mouth close)
        # Logic for Yawning (Immediate Trigger)
        if mar > MOUTH_AR_THRESH:
            if yawn_start is None: 
                yawn_start = time.time()
            
            yawn_duration = time.time() - yawn_start
            
            # If mouth has been open for > 2 seconds
            if yawn_duration > YAWN_LIMIT:
                if not yawn_debounce:
                    yawn_counter += 1
                    yawn_debounce = True # Locks the counter so it stays at +1
                
                # Trigger alarm IMMEDIATELY on the 3rd yawn
                if yawn_counter >= 3:
                    driver_status = "YAWNING"
                    trigger_alarm()
        else:
            # Mouth is closed: reset the timer and unlock the counter
            yawn_start = None
            yawn_debounce = False 
            if driver_status == "YAWNING" and not alarm_active:
                driver_status = "NORMAL"
        if eye_closed_start is None and mar <= MOUTH_AR_THRESH:
            if not alarm_active: driver_status = "NORMAL"

    # 2. HAND ANALYSIS
    thumb_detected_this_frame = False
    if hand_res.multi_hand_landmarks:
        for hand_lms in hand_res.multi_hand_landmarks:
            if show_mesh:
                mp_drawing.draw_landmarks(frame, hand_lms, mp_hands.HAND_CONNECTIONS, mp_drawing_styles.get_default_hand_landmarks_style(), mp_drawing_styles.get_default_hand_connections_style())
            
            if alarm_active and is_thumbs_up(hand_lms):
                thumb_detected_this_frame = True
                
                # Start timer if not already started
                if thumb_confirm_start is None:
                    thumb_confirm_start = time.time()
                else:
                    hold_duration = time.time() - thumb_confirm_start
                    
                    # Visual feedback: Show how much longer to hold
                    remaining = max(0, 1.0 - hold_duration)
                    cv2.putText(frame, f"HOLD: {remaining:.1f}s", (w-200, h-100), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

                    # If held for 1 second, stop alarm
                    if hold_duration > 1.0:
                        alarm_active = False
                        if alarm_sound: alarm_sound.stop()
                        driver_status = "NORMAL"
                        thumb_confirm_start = None 
    
    # If no thumbs up is seen in the current frame, reset the hold timer
    if not thumb_detected_this_frame:
        thumb_confirm_start = None

    # 3. AUTO-STOP ALARM (25 Seconds)
    if alarm_active and alarm_start_time:
        if (time.time() - alarm_start_time) > 25.0:
            alarm_active = False
            if alarm_sound: alarm_sound.stop()

    # 4. UI OVERLAY
    color = (0, 255, 0) if driver_status == "NORMAL" else (0, 0, 255)
    cv2.putText(frame, f"STATUS: {driver_status}", (20, 50), 1, 2, color, 2)
    cv2.putText(frame, f"YAWNS: {yawn_counter}", (20, 90), 1, 2, (255, 255, 0), 2)
    cv2.putText(frame, f"EAR: {ear:.2f} | MAR: {mar:.2f}", (20, 130), 1, 1.5, (255, 255, 255), 2)
    cv2.putText(frame, "Press 'V' to toggle Mesh | 'Q' to Quit", (20, h-20), 1, 1, (200, 200, 200), 1)

    if alarm_active:
        cv2.rectangle(frame, (10, h-80), (w-10, h-40), (0,0,255), -1)
        cv2.putText(frame, "ALARM ACTIVE - THUMBS UP TO STOP", (30, h-50), 1, 1.5, (255,255,255), 2)

    cv2.imshow("DMS - Stable Build", frame)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'): break
    if key == ord('v'): show_mesh = not show_mesh # Toggle visual meshes

cap.release()
cv2.destroyAllWindows()
pygame.mixer.quit()