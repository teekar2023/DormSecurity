import time
import subprocess
import pyperclip
import sys


def run_ngrok():
    ngrok_process = subprocess.Popen(['ngrok', 'http', '8080'])
    time.sleep(3)
    url = "http://127.0.0.1:4040/api/tunnels"
    tunnel_info = subprocess.check_output(["curl", url]).decode("utf-8")
    public_url = tunnel_info.split('"public_url":"')[1].split('"')[0]
    return public_url, ngrok_process


ngrok_url, n_process = run_ngrok()
app_process = subprocess.Popen(['/Users/sreekarpalla/IdeaProjects/DormSecurity/venv/bin/python', '/Users/sreekarpalla/IdeaProjects/DormSecurity/SecuritySystemServer.py'])
pyperclip.copy(ngrok_url)
print(ngrok_url)
try:
    app_process.wait()
    pass
except KeyboardInterrupt:
    pass

try:
    app_process.kill()
    pass
except Exception:
    pass
n_process.kill()
sys.exit(0)
