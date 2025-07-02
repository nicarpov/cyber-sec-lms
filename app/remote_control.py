from uuid import uuid4
from fabric import Connection, Config
import os
from pathlib import Path
from sys import platform

host = '192.168.0.119'
# host_remote = '89.109.5.245'
port = 8020
user = 'arapov'
config = Config(overrides={'sudo': {'password': '1opoWE_vdo'}})


def backup(host: str, comment: str, backup_dir: str, link_path: str = None):
    uid = uuid4()
    path = os.path.join(backup_dir, str(uid)) + os.sep

    if platform == 'win32':
        path = Path(path).as_posix()

    link_option = "--link-dest={}"
    link_dest = link_option.format(link_path) if link_path else ''
    backup_cmd = "rsync -aAXv --rsync-path='mkdir {1}' --progress --exclude={'{0}*','/dev/*','/proc/*','/sys/*','/tmp/*','/run/*','/mnt/*','/media/*','/lost+found'} \
                    {2} / {1}".format(backup_dir, path, link_dest)
    # conn = Connection(host=host, user=user, port=22, config=config)
    # result = conn.run('pwd', hide=True)
    # print(result.stdout)
    try:
        # result = conn.sudo(backup_cmd, hide=True)
        # print(result.stdout)
        print(backup_cmd)
    except Exception as err:
        print(err)
    return {"backup_id": uid,
            "host": host,
            "comment": comment,
            }