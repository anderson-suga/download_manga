import os

from dotenv import load_dotenv

load_dotenv()

config = {
    "URL": os.getenv("URL"),
    "URL_LOGIN": os.getenv("URL_LOGIN"),
    "URL_PWD": os.getenv("URL_PWD"),
    "WAIT_TIME": os.getenv("WAIT_TIME"),
    "SCREEN_SIZE": os.getenv("SCREEN_SIZE"),
    "CHROME_DRIVER": os.getenv("CHROME_DRIVER"),
    "CHROME_PROCESS_NAME": os.getenv("CHROME_PROCESS_NAME"),
    "PROFILE_PATH": os.getenv("PROFILE_PATH"),
    "EXTENSION_PATH": os.getenv("EXTENSION_PATH"),
    "DB_HOST": os.getenv("DB_HOST"),
    "DB_PORT": os.getenv("DB_PORT"),
    "DB_NAME": os.getenv("DB_NAME"),
    "DB_USR": os.getenv("DB_USR"),
    "DB_PWD": os.getenv("DB_PWD"),
    "GITHUB_URL": os.getenv("GITHUB_URL"),
    "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN"),
    "URL_404": os.getenv("URL_404"),
    "LOG_DIRECTORY": os.getenv("LOG_DIRECTORY"),
    "GDRIVE_DIRECTORY": os.getenv("GDRIVE_DIRECTORY"),
    "TEMP_DIRECTORY": os.getenv("TEMP_DIRECTORY"),
    "NOT_FOUND": os.getenv("NOT_FOUND"),
}
