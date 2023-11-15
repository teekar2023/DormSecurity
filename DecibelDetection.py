import sounddevice as sd
import numpy as np
from datetime import datetime
import time
import soundfile as sf
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import json


settings = json.load(open("/Users/sreekarpalla/IdeaProjects/DormSecurity/Settings/settings.json", "r"))
SAMPLE_RATE = 44100
loud_sound_threshold = settings["loud_sound_threshold"]
really_loud_sound_threshold = settings["really_loud_sound_threshold"]
sound_detection_cooldown = settings["sound_detection_cooldown"]
logs_dir = settings["logs_dir"]
cap_dir = settings["captures_dir"]
email_password = settings["email_password"]
log_file_path = f"{logs_dir}DecibelLogs.txt"
audio_file_path = f"{cap_dir}loud_sound_recording.wav"
last_detection = 0.0


def send_email(subject, body, attachment_path):
    sender_email = "sree23palla@icloud.com"
    sender_password = email_password
    recipient_email = "sree23palla@gmail.com"

    message = MIMEMultipart()
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = recipient_email
    message.attach(MIMEText(body, "plain"))

    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(attachment_path)}")
            message.attach(part)

        with smtplib.SMTP("smtp.mail.me.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, message.as_string())


def callback(indata, frames, t, status):
    global last_detection
    log_file = open(log_file_path, "r+")
    current_logs = log_file.read()
    if time.time() - last_detection >= sound_detection_cooldown:
        last_detection = time.time()
        pass
    else:
        return
    if np.max(np.abs(indata)) >= 0.80:
        timestamp = time.time()
        dt_object = datetime.fromtimestamp(timestamp)
        formatted_time = dt_object.strftime('%Y-%m-%d %H:%M:%S')
        print(f"Extremely Loud Sound Detected: {formatted_time}")
        if formatted_time not in current_logs:
            log_file.truncate()
            log_file.write(f"Extremely Loud Sound Detected: {formatted_time}\n" + current_logs)
        sf.write(audio_file_path, indata, SAMPLE_RATE)
        send_email("Extremely Loud Noise!!!",
                   f"An extremely loud noise was detected at {formatted_time}. Check the attached audio recording to hear it.",
                   audio_file_path)
        pass
    elif np.max(np.abs(indata)) >= really_loud_sound_threshold:
        timestamp = time.time()
        dt_object = datetime.fromtimestamp(timestamp)
        formatted_time = dt_object.strftime('%Y-%m-%d %H:%M:%S')
        print(f"Really Loud Sound Detected: {formatted_time}")
        if formatted_time not in current_logs:
            log_file.truncate()
            log_file.write(f"Loud Sound Sound Detected: {formatted_time}\n" + current_logs)
        sf.write(audio_file_path, indata, SAMPLE_RATE)
        send_email("Loud Noise Alert",
                   f"A really loud noise was detected at {formatted_time}. Check the attached audio recording to hear it.",
                   audio_file_path)
        pass
    elif np.max(np.abs(indata)) >= loud_sound_threshold:
        timestamp = time.time()
        dt_object = datetime.fromtimestamp(timestamp)
        formatted_time = dt_object.strftime('%Y-%m-%d %H:%M:%S')
        print(f"Sound Detected: {formatted_time}")
        if formatted_time not in current_logs:
            log_file.truncate()
            log_file.write(f"Sound Detected: {formatted_time}\n" + current_logs)
        pass
    else:
        pass


with sd.InputStream(callback=callback, channels=1, samplerate=SAMPLE_RATE):
    print("Listening for noises.")
    while True:
        time.sleep(1.5)
        pass
