import subprocess
from src.config.config import config

def close_chrome():
    try:
        chrome_process = config["CHROME_PROCESS_NAME"]

        resultado = subprocess.run(["pgrep", chrome_process], capture_output=True, text=True)

        if resultado.stdout:
            print("Google Chrome is running. Closing...")
            subprocess.run(["pkill", "-9", chrome_process])
            print("Google Chrome closed successfully!")
        else:
            print("Google Chrome is not running.")

        return True

    except Exception as e:
        print(f"Error checking or closing Chrome:\n{e}")
        return False
