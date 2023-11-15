import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import cv2
import time
import json


def capture_and_save_image(file_path):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return None
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(f"{cap_dir}" + file_path, frame)
    cap.release()
    return f"{cap_dir}" + file_path


settings = json.load(open("/Users/sreekarpalla/IdeaProjects/DormSecurity/Settings/settings.json"))
cap_dir = settings["captures_dir"]
email_password = settings["email_password"]
sender_email = "sree23palla@icloud.com"
recipient_email = "sree23palla@gmail.com"
subject = "Security System Alert"
body = "Motion Detected In Dorm"
msg = MIMEMultipart()
msg["From"] = sender_email
msg["To"] = recipient_email
msg["Subject"] = subject
msg.attach(MIMEText(body, "plain"))
image_file = capture_and_save_image("captured_image.jpg")
if image_file:
    with open(image_file, "rb") as image_data:
        image = MIMEImage(image_data.read())
        image.add_header("Content-Disposition", f"attachment; filename={image_file}")
        msg.attach(image)
time.sleep(2)
image_file_two = capture_and_save_image("captured_image2.jpg")
if image_file_two:
    with open(image_file_two, "rb") as image_data:
        image = MIMEImage(image_data.read())
        image.add_header("Content-Disposition", f"attachment; filename={image_file_two}")
        msg.attach(image)
smtp_server = "smtp.mail.me.com"
smtp_port = 587
try:
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender_email, email_password)
    server.sendmail(sender_email, recipient_email, msg.as_string())
    print("Email notification sent!!!")
except Exception as e:
    print(f"An error occurred: {str(e)}")
finally:
    server.quit()
