from src.config.config import config

connection_info = {
    "host": config["DB_HOST"],
    "port": config["DB_PORT"],
    "dbname": config["DB_NAME"],
    "user": config["DB_USR"],
    "password": config["DB_PWD"],
}
