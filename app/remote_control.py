from uuid import uuid4
from fabric import Connection, Config
import os
from pathlib import Path
from sys import platform
from remote_ctl_config import PKEY_PATH

host = '192.168.1.12'
# host_remote = '89.109.5.245'
port = 22
user = 'remote'
config = Config(overrides={'sudo': {'password': '123'}})


def backup(conn: Connection, comment: str, backup_dir: str, link_path: str = None):
    """Makes backup of files in Linux-based system
    
    conn
        SSH connection object returned from Connection func of Fabric library
    """
    uid = str(uuid4())
    
    if backup_dir[-1] != '/':
        backup_dir = backup_dir + '/'
    path = os.path.join(backup_dir, uid) + os.sep

    if platform == 'win32':
        path = Path(path).as_posix()
    if path[-1] != '/':
        path = path + '/'
    link_option = " --link-dest={}"
    link_dest = link_option.format(link_path) if link_path else ''
    backup_cmd = "rsync -aAXv --rsync-path='mkdir {path}' --progress --exclude={{'{backup_dir}*','/dev/*','/proc/*','/sys/*','/tmp/*','/run/*','/mnt/*','/media/*','/lost+found'}}{link_dest} / {path}".format(backup_dir=backup_dir, path=path, link_dest=link_dest)
    
    
    
    try:
        result = conn.sudo(backup_cmd, hide=True)
        
        
    except Exception as err:
        return {"backup_id": uid,
            "host": conn.host,
            "backup_cmd": backup_cmd,
            "link_path": link_path or "",
            "path": path,
            "comment": comment,
            "cmd_result": '',
            "cmd_error": repr(err),
            "cmd_code": 1
            }
    
    return {"backup_id": uid,
            "host": conn.host,
            "backup_cmd": backup_cmd,
            "link_path": link_path or "",
            "path": path,
            "comment": comment,
            "cmd_error": result.stderr,
            "cmd_code": result.exited
            }


def main():
    print(f"Connect using {PKEY_PATH}")
    with Connection(
        host=host, 
        user=user, 
        port=22, 
        config=config, 
        connect_kwargs={
            "key_filename": PKEY_PATH
            }
    ) as conn:
        res = backup(conn, "test", "/backup")
        print(res)


if __name__ == "__main__":
    main()