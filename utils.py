import subprocess

def notify(title, message, expire_time=2000, urgency="normal"):
    subprocess.run([
        "notify-send",
        "-u", urgency,
        "-t", str(expire_time),
        title,
        message
    ])
