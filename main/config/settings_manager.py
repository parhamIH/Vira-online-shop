# settings_manager.py

from dotenv import load_dotenv
import os

class Settings:
    def __init__(self):
        load_dotenv()

        self.db_engine = os.getenv('DB_ENGINE')
        self.db_name = os.getenv('DB_NAME')
        self.db_user = os.getenv('DB_USER')
        self.db_password = os.getenv('DB_PASSWORD')
        self.db_host = os.getenv('DB_HOST')
        self.db_port = int(os.getenv('DB_PORT', 3306)) # تبدیل به اینتجر

        self.zarinpal_merchant_id = os.getenv('ZARINPAL_MERCHANT_ID')
        self.zarinpal_sandbox = os.getenv('ZARINPAL_SANDBOX', 'True').lower() == 'true' # تبدیل به بولین

        self.secret_key = os.getenv('SECRET_KEY')
        self.allowed_hosts = eval(os.getenv('ALLOWED_HOSTS', '["*"]')) # تبدیل به لیست

settings_instance = Settings()

