import os
import dotenv

dotenv.load_dotenv()

REDIS_HOST = os.environ.get('REDIS_HOST') or '127.0.0.1'
REDIS_PORT = os.environ.get('REDIS_PORT') or 6379
REDIS_DB = os.environ.get('REDIS_DB') or 0
