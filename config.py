# config.py
from decouple import config

DEFAULT_API = config("DEFAULT_API")

WAREHOUSE_API_URL = config("WAREHOUSE_API_URL")
CLIENT_API_URL = config("CLIENT_API_URL")

DB_NAME = config("DB_NAME")
DB_USER = config("DB_USER")
DB_PASS = config("DB_PASS")
DB_HOST = config("DB_HOST")
DB_PORT = config("DB_PORT")


DRF_API_URL_FILE = config("DRF_API_URL_FILE")
SOCIAL_MEDIA_API_URL = config("SOCIAL_MEDIA_API_URL")
CONTACT_API_URL = config("CONTACT_API_URL")

ORDER_API = config("ORDER_API")
