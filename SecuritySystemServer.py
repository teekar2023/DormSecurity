from flask import Flask, render_template, request, redirect, url_for, Response
from subprocess import Popen
import socket
import pyperclip
import subprocess
import sys
import os
import signal
import psutil
import json

app = Flask(__name__)

motion_detection = False
motion_detection_process = None
decibel_detection = False
decibel_detection_process = None
alarm_system_on = False
alarm_system_process = None
recording_process = None
recording = False
notification = ""

settings_file_json = open("/Users/sreekarpalla/IdeaProjects/DormSecurity/Settings/settings.json", "r")
settings_json = json.load(settings_file_json)
log_path = settings_json["logs_dir"]
server_port = settings_json["port"]


def get_battery_percent():
    battery = psutil.sensors_battery()
    percent = battery.percent
    return percent


@app.route('/')
def index():
    return render_template('index.html', motion_detected=motion_detection, decibel_detection=decibel_detection,
                           alarm_system_on=alarm_system_on, battery_percent=get_battery_percent(),
                           notifcation_message=notification, recording_video=recording)


@app.route('/start_motion_detection')
def start_motion_detection():
    global motion_detection_process, motion_detection, notification
    if motion_detection:
        notification = "Motion detection is already active"
        return redirect(url_for("index", notification_message=notification))
    else:
        motion_detection_process = Popen(['/Users/sreekarpalla/IdeaProjects/DormSecurity/venv/bin/python',
                                          '/Users/sreekarpalla/IdeaProjects/DormSecurity/MotionDetectionScript.py'])
        motion_detection = True
        print("Started motion detection")
        notification = "Started motion detection."
        return redirect(url_for("index", notification_message=notification))


@app.route('/stop_motion_detection')
def stop_motion_detection():
    global motion_detection_process, motion_detection, notification
    if motion_detection_process:
        try:
            motion_detection_process.kill()
            motion_detection_process = None
            motion_detection = False
        except Exception:
            pass
        print("Stopped motion detection")
        notification = "Stopped motion detection."
        return redirect(url_for("index", notification_message=notification))
    else:
        notification = "Motion detection is not active."
        return redirect(url_for("index", notification_message=notification))


@app.route("/clearMotionLogs")
def clear_motion_logs():
    with open(f"{log_path}MotionLogs.txt", "w") as file:
        file.close()
    return render_template("motionDetection.html", motion_detected=motion_detection,
                           logs_text=open(f"{log_path}MotionLogs.txt",
                                          "r").read())


@app.route("/clearDecibelLogs")
def clear_decibel_logs():
    with open(f"{log_path}DecibelLogs.txt", "w") as file:
        file.close()
    return render_template("decibelDetection.html", decibel_detection=decibel_detection,
                           logs_text=open(f"{log_path}DecibelLogs.txt",
                                          "r").read())


@app.route("/viewMotionLogs")
def motion_logs():
    return render_template("motionDetection.html", motion_detected=motion_detection,
                           logs_text=open(f"{log_path}MotionLogs.txt",
                                          "r").read())


@app.route("/viewDecibelLogs")
def decibel_logs():
    return render_template("decibelDetection.html", decibel_detection=decibel_detection,
                           logs_text=open(f"{log_path}DecibelLogs.txt",
                                          "r").read())


@app.route("/start_decibel_detection")
def start_decibel_detection():
    global decibel_detection, decibel_detection_process, notification
    if decibel_detection:
        notification = "Sound detection is already active."
        return redirect(url_for("index", notification_message=notification))
    else:
        decibel_detection_process = Popen(['/Users/sreekarpalla/IdeaProjects/DormSecurity/venv/bin/python',
                                           '/Users/sreekarpalla/IdeaProjects/DormSecurity/DecibelDetection.py'])
        decibel_detection = True
        print("Started decibel detection")
        notification = "Started sound detection."
        return redirect(url_for("index", notification_message=notification))


@app.route("/viewAlarmPage")
def view_alarm_page():
    return render_template("alarmSystem.html", alarm_system_on=alarm_system_on)


@app.route("/stop_decibel_detection")
def stop_decibel_detection():
    global decibel_detection, decibel_detection_process, notification
    if decibel_detection_process:
        try:
            decibel_detection_process.kill()
            decibel_detection_process = None
            decibel_detection = False
        except Exception:
            notification = "New settings saved."
            return redirect(url_for("index", notification_message=notification))
        print("Stopped decibel detection")
        notification = "Stopped sound detection."
        return redirect(url_for("index", notification_message=notification))
    else:
        notification = "Sound detection is not active."
        return redirect(url_for("index", notification_message=notification))


@app.route('/activate_alarm')
def activate_alarm():
    global alarm_system_on, alarm_system_process, notification
    print("Activating alarm")
    try:
        subprocess.run(["osascript", "-e", "set volume output volume 100"])
        alarm_system_process = Popen(['/Users/sreekarpalla/IdeaProjects/DormSecurity/venv/bin/python',
                                        '/Users/sreekarpalla/IdeaProjects/DormSecurity/AlarmSystem.py'])
        alarm_system_on = True
        return render_template("alarmSystem.html", alarm_system_on=alarm_system_on)
    except Exception as e:
        return render_template("alarmSystem.html", alarm_system_on=alarm_system_on)


@app.route('/deactivate_alarm')
def deactivate_alarm():
    global alarm_system_process, alarm_system_on
    print("Deactivating alarm")
    subprocess.run(["osascript", "-e", "set volume output volume 25"])
    try:
        alarm_system_process.kill()
    except Exception:
        pass
    alarm_system_process = None
    alarm_system_on = False
    return render_template("alarmSystem.html", alarm_system_on=alarm_system_on)


@app.route("/monitorCamera")
def monitor_camera():
    return render_template("monitorCamera.html")  # TODO


@app.route("/remoteDesktop")
def remote_desktop():
    return redirect("http://remotedesktop.google.com")


@app.route("/settings")
def settings_page():
    print("Showing settings page")
    settings_file = open("/Users/sreekarpalla/IdeaProjects/DormSecurity/Settings/settings.json", "r")
    settings = json.load(settings_file)
    settings_file.close()
    loud_sound_threshold = settings["loud_sound_threshold"]
    really_loud_sound_threshold = settings["really_loud_sound_threshold"]
    motion_detection_email_cooldown = settings["motion_detection_email_cooldown"]
    motion_detection_cooldown = settings["motion_detection_cooldown"]
    sound_detection_cooldown = settings["sound_detection_cooldown"]
    captures_dir = settings["captures_dir"]
    logs_dir = settings["logs_dir"]
    recordings_dir = settings["recordings_dir"]
    email_password = settings["email_password"]
    port = settings["port"]
    return render_template("settings.html", loud_sound_threshold=loud_sound_threshold,
                           really_loud_sound_threshold=really_loud_sound_threshold,
                           motion_detection_email_cooldown=motion_detection_email_cooldown,
                           sound_detection_cooldown=sound_detection_cooldown,
                           motion_detection_cooldown=motion_detection_cooldown, captures_path=captures_dir,
                           logs_path=logs_dir, recordings_path=recordings_dir, email_password=email_password, port=port)


@app.route('/saveSettings', methods=['POST'])
def save_new_settings():
    global notification
    if request.method == 'POST':
        loud_sound_threshold = float(request.form['loudSoundThreshold'])
        really_loud_sound_threshold = float(request.form['reallyLoudSoundThreshold'])
        sound_detection_cooldown = float(request.form['soundDetectionCooldown'])
        motion_detection_email_cooldown = float(request.form['motionDetectionEmailCooldown'])
        motion_detection_cooldown = float(request.form['motionDetectionCooldown'])
        captures_dir = str(request.form['capturesPath'])
        logs_dir = str(request.form['logsPath'])
        recordings_dir = str(request.form['recordingsPath'])
        email_password = str(request.form['emailPassword'])
        port = int(request.form['port'])
        data = {
            "loud_sound_threshold": loud_sound_threshold,
            "really_loud_sound_threshold": really_loud_sound_threshold,
            "sound_detection_cooldown": sound_detection_cooldown,
            "motion_detection_email_cooldown": motion_detection_email_cooldown,
            "motion_detection_cooldown": motion_detection_cooldown,
            "captures_dir": captures_dir,
            "logs_dir": logs_dir,
            "recordings_dir": recordings_dir,
            "email_password": email_password,
            "port": port
        }
        with open("/Users/sreekarpalla/IdeaProjects/DormSecurity/Settings/settings.json", "w") as f:
            json.dump(data, f)
        f.close()
        notification = "New settings saved."
        return redirect(url_for("index", notification_message=notification))


@app.route("/startAllSystems")
def start_all_systems():
    global notification
    global motion_detection_process, motion_detection, decibel_detection, decibel_detection_process
    motion_detection_process = Popen(['/Users/sreekarpalla/IdeaProjects/DormSecurity/venv/bin/python',
                                      '/Users/sreekarpalla/IdeaProjects/DormSecurity/MotionDetectionScript.py'])
    motion_detection = True
    print("Started motion detection")
    decibel_detection_process = Popen(['/Users/sreekarpalla/IdeaProjects/DormSecurity/venv/bin/python',
                                       '/Users/sreekarpalla/IdeaProjects/DormSecurity/DecibelDetection.py'])
    decibel_detection = True
    print("Started decibel detection")
    notification = "Started all detection systems."
    return redirect(url_for("index", notification_message=notification))


@app.route("/stopAllSystems")
def stop_all_systems():
    global motion_detection_process, motion_detection, decibel_detection, decibel_detection_process, notification
    try:
        motion_detection_process.kill()
        motion_detection_process = None
        motion_detection = False
    except Exception:
        pass
    print("Stopped motion detection")
    try:
        decibel_detection_process.kill()
        decibel_detection_process = None
        decibel_detection = False
    except Exception:
        pass
    print("Stopped decibel detection")
    notification = "Stopped all detection systems."
    return redirect(url_for("index", notification_message=notification))


@app.route("/shutdown_server")
def shutdown_server():
    global motion_detection_process, decibel_detection_process, alarm_system_process
    try:
        motion_detection_process.kill()
        motion_detection_process = None
    except Exception:
        pass
    print("Stopped motion detection")
    try:
        decibel_detection_process.kill()
        decibel_detection_process = None
    except Exception:
        pass
    print("Stopped decibel detection")
    print("Deactivating alarm")
    subprocess.run(["osascript", "-e", "set volume output volume 25"])
    try:
        alarm_system_process.kill()
    except Exception:
        pass
    alarm_system_process = None
    print("Shutting down server.")
    subprocess.run('pkill -9 -f Terminal', shell=True)
    subprocess.run('pkill -9 -f StartSecurityServer', shell=True)
    subprocess.run('pkill -9 -f python', shell=True)
    subprocess.run('pkill -9 -f ngrok', shell=True)
    os.kill(os.getpid(), signal.SIGINT)
    return redirect(f"http://{socket.gethostbyname(socket.gethostname())}:8080")


@app.route("/restart_server")
def restart_server():
    global motion_detection_process, decibel_detection_process, alarm_system_process
    try:
        motion_detection_process.kill()
        motion_detection_process = None
    except Exception:
        pass
    print("Stopped motion detection")
    try:
        decibel_detection_process.kill()
        decibel_detection_process = None
    except Exception:
        pass
    print("Stopped decibel detection")
    print("Deactivating alarm")
    subprocess.run(["osascript", "-e", "set volume output volume 25"])
    try:
        alarm_system_process.kill()
    except Exception:
        pass
    alarm_system_process = None
    print("Restarting server.")
    python = sys.executable
    os.execl(python, python, *sys.argv)


@app.route("/viewVideoRecordings")
def view_video_recordings():
    return render_template("videoRecordings.html")


@app.route("/startRecording")
def start_recording():
    global motion_detection_process, motion_detection, decibel_detection, decibel_detection_process, notification, recording, recording_process
    try:
        motion_detection_process.kill()
        motion_detection_process = None
        motion_detection = False
    except Exception:
        pass
    print("Stopped motion detection")
    try:
        decibel_detection_process.kill()
        decibel_detection_process = None
        decibel_detection = False
    except Exception:
        pass
    print("Stopped decibel detection")
    recording_process = Popen(['/Users/sreekarpalla/IdeaProjects/DormSecurity/venv/bin/python',
                               '/Users/sreekarpalla/IdeaProjects/DormSecurity/RecordVideo.py'])
    recording = True
    print("Started recording")
    notification = "Stopped all systems and started recording."
    return redirect(url_for("index", notification_message=notification))


@app.route("/stopRecording")
def stop_recording():
    global recording_process, recording, notification
    try:
        recording_process.kill()
        recording_process = None
        recording = False
    except Exception:
        pass
    print("Recording stopped.")
    notification = "Stopped recording."
    return redirect(url_for("index", notification_message=notification))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(server_port), debug=True)
