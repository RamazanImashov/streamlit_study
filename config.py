# config.py
from decouple import config

MONGODB_URL = config("MONGODB_URL", default="mongodb://mongodb:27017")
WAREHOUSE_API_URL = config("WAREHOUSE_API_URL")
CLIENT_API_URL = config("CLIENT_API_URL")
WKHTMLTOIMAGE_PATH = config("WKHTMLTOIMAGE_PATH", default="/usr/local/bin/wkhtmltoimage")

DB_NAME = config("DB_NAME")
DB_USER = config("DB_USER")
DB_PASS = config("DB_PASS")
DB_HOST = config("DB_HOST")
DB_PORT = config("DB_PORT")
