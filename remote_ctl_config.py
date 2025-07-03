import os
import dotenv

dotenv.load_dotenv()

PKEY_PATH = os.environ.get('PKEY_PATH') or '/home/user/.ssh/id_rsa'