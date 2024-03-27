import time
import subprocess
import os


def control():
    while True:
        subprocess.Popen(["python", "web_img_analyse.py"])
        time.sleep(60)
        os.system("taskkill /F /IM python.exe")
        time.sleep(10)


if __name__ == "__main__":
    control()
