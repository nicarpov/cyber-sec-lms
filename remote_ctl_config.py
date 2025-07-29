import os
import dotenv

dotenv.load_dotenv()

class RemoteCtlConf():
    PKEY_PATH = os.environ.get('PKEY_PATH') or '/home/user/.ssh/id_rsa'
    REMOTE_USER = os.environ.get('REMOTE_USER') or 'remote'
    REMOTE_PORT = os.environ.get('REMOTE_PORT') or 22
    SUDO_PASS = os.environ.get('SUDO_PASS') or '123'
    BACKUP_DIR =os.environ.get('REMOTE_BACKUP_DIR') or '/backup'