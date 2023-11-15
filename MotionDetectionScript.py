import cv2
import time
import os
import json
from datetime import datetime


def on_motion_detected():
    global last_detection
    if last_detection is None:
        last_detection = time.time()
        return
    elif time.time() - float(last_detection) >= motion_detection_email_cooldown and time.time() - float(
            last_detection) >= motion_detection_cooldown:
        last_detection = time.time()
        dt_object = datetime.fromtimestamp(last_detection)
        formatted_time = dt_object.strftime('%Y-%m-%d %H:%M:%S')
        print("Motion detected: " + str(formatted_time))
        log_file = open(f"{logs_dir}MotionLogs.txt", "r+")
        old_logs = log_file.read()
        log_file.write("Motion detected: " + str(formatted_time) + "\n" + old_logs)
        log_file.close()
        os.system(
            "/Users/sreekarpalla/IdeaProjects/DormSecurity/venv/bin/python /Users/sreekarpalla/IdeaProjects/DormSecurity/SendEmailNotification.py")
        return
    elif time.time() - float(last_detection) >= motion_detection_cooldown:
        last_detection = time.time()
        dt_object = datetime.fromtimestamp(time.time())
        formatted_time = dt_object.strftime('%Y-%m-%d %H:%M:%S')
        print("Motion detected: " + str(formatted_time))
        log_file = open(f"{logs_dir}MotionLogs.txt", "r+")
        old_logs = log_file.read()
        log_file.write("Motion detected: " + str(formatted_time) + "\n" + old_logs)
        log_file.close()
        return
    else:
        return


settings = json.load(open("/Users/sreekarpalla/IdeaProjects/DormSecurity/Settings/settings.json"))
motion_detection_cooldown = settings["motion_detection_cooldown"]
motion_detection_email_cooldown = settings["motion_detection_email_cooldown"]
logs_dir = settings["logs_dir"]
cap_dir = settings["captures_dir"]
cap = cv2.VideoCapture(0)
ret, frame1 = cap.read()
if not ret:
    cap.release()
    raise Exception("Failed to access camera.")
frame1_gray = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
frame1_blurred = cv2.GaussianBlur(frame1_gray, (25, 25), 0)

motion_detected = False
last_detection = None

while True:
    time.sleep(1)
    ret, frame2 = cap.read()
    if not ret:
        break
    frame2_gray = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    frame2_blurred = cv2.GaussianBlur(frame2_gray, (25, 25), 0)
    frame_diff = cv2.absdiff(frame1_blurred, frame2_blurred)
    _, thresh = cv2.threshold(frame_diff, 10, 255, cv2.THRESH_BINARY)
    thresh = cv2.dilate(thresh, None, iterations=2)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        if cv2.contourArea(contour) > 500:
            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(frame2, (x, y), (x + w, y + h), (0, 0, 255), 2)
            motion_detected = True
    cv2.imshow("Dorm Security Motion Detection", frame2)
    frame1_blurred = frame2_blurred
    if motion_detected:
        on_motion_detected()
        motion_detected = False

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
