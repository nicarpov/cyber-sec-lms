from uuid import uuid4
from fabric import Connection, Config, SerialGroup
import os
from pathlib import Path
from sys import platform

from remote_ctl_config import RemoteCtlConf

# host = '192.168.1.12'
# host_remote = '89.109.5.245'


class SSHConn(Connection):
    """SSHConn - connection class specialized for using with preconfigured parameters
    
    user, port, key_filename and sudo password are configured accordingly by 
    REMOTE_USER, REMOTE_PORT, PKEY_PATH and SUDO_PASS config parameters
    """

    def __init__(self, host, conf=RemoteCtlConf):
        super().__init__(
            host, 
            user=conf.REMOTE_USER, 
            port=conf.REMOTE_PORT, 
            config=Config(
                overrides={
                    'sudo': {'password': conf.SUDO_PASS,
                            }
                    }
                ), 
            connect_kwargs={
                        "key_filename": conf.PKEY_PATH
                        }
        )



def backup(host, backup_uid: str, comment: str, backup_dir: str = RemoteCtlConf.BACKUP_DIR, link_path: str = None):
    """Makes backup of files in Linux-based system"""
    
    if backup_dir[-1] != '/':
        backup_dir = backup_dir + '/'
    path = os.path.join(backup_dir, backup_uid) + os.sep

    if platform == 'win32':
        path = Path(path).as_posix()
    if path[-1] != '/':
        path = path + '/'

    link_option = " --link-dest={}"
    link_dest = link_option.format(link_path) if link_path else ''

    backup_cmd = "rsync -aAXv " \
    "--rsync-path='mkdir {path}' " \
    "--exclude={{'{backup_dir}*','/dev/*','/proc/*','/sys/*','/tmp/*','/run/*','/mnt/*','/media/*','/lost+found'}}" \
    "{link_dest} / {path}".format(backup_dir=backup_dir, path=path, link_dest=link_dest)
    
    try:
        # with SSHConn(host=host) as conn:
        #     result = conn.sudo(backup_cmd, hide=True)
        pass
    except Exception as err:
        return {"backup_id": backup_uid,
            "host": host,
            "backup_cmd": backup_cmd,
            "link_path": link_path or "",
            "path": path,
            "comment": comment,
            "cmd_result": '',
            "cmd_error": repr(err),
            "cmd_code": 1
            }
    
    return {"backup_id": backup_uid,
            "host": host,
            "backup_cmd": backup_cmd,
            "link_path": link_path or "",
            "path": path,
            "comment": comment,
            # "cmd_error": result.stderr,
            # "cmd_code": result.exited
            }


def restore(host, backup_uid: str, backup_dir: str = RemoteCtlConf.BACKUP_DIR):
    """Restores backup of files in Linux-based system
        path - path to backup dir
    """
    if backup_dir[-1] != '/':
        backup_dir = backup_dir + '/'
    path = os.path.join(backup_dir, backup_uid) + os.sep

    if platform == 'win32':
        path = Path(path).as_posix()
    if path[-1] != '/':
        path = path + '/'
    
    print("Path: ", path)
    backup_cmd = "rsync -aAXv --delete " \
                "--exclude={{'{backup_dir}*','/dev/*','/proc/*','/sys/*','/tmp/*','/run/*','/mnt/*','/media/*','/lost+found'}} " \
                "{path} /".format(path=path, backup_dir=backup_dir)
    
    try:
        with SSHConn(host=host) as conn:
            result = conn.sudo(backup_cmd, hide=True)
        
    except Exception as err:
        return {"backup_id": backup_uid,
            "host": host,
            "restore_cmd": backup_cmd,
            "path": path,
            "cmd_result": '',
            "cmd_error": repr(err),
            "cmd_code": 1
            }
    
    return {"backup_id": backup_uid,
            "host": host,
            "backup_cmd": backup_cmd,
            "path": path,
            "cmd_error": result.stderr,
            "cmd_code": result.exited
            }

def isAvailable(host):
    isOnline = False
    errMsg = ''
    try:
        with SSHConn(host=host) as conn:
            res = conn.open()
            isOnline = True
        
    except Exception as err:
        errMsg = str(err)
    if isOnline:

        return {
                "isOnline" : "yes"
                }
    else:
        return {
                "isOnline" : "no",
                "err": errMsg
                }
    

def reboot(host):
    cmd = f"shutdown -r"
    try:
        with SSHConn(host=host) as conn:
            # print('SSHConn', conn.config.sudo)
            result = conn.sudo(cmd, hide=True)
            # print('reboot res:', result)
        
    except Exception as err:
        return {
            "host": host,
            "cmd": cmd,
            "cmd_result": '',
            "cmd_error": repr(err),
            "cmd_code": 1
            }
    
    return {
            "host": host,
            "cmd": cmd,
            "cmd_result": '',
            "cmd_code": 0
            }

def search_hosts(nmap_target):
    host_list = []
    try:
        with SSHConn(host='localhost') as conn:
            res = conn.sudo('nmap -sn {} -oG -'.format(nmap_target), hide=True)
            lines = res.stdout.split('\n')
            host_lines = list(filter(lambda l: l.startswith('Host:'), lines))
            host_list = [line.split()[1] for line in host_lines]
        return host_list
    except:
        return []
        

def main():
    print(f"Connect using {RemoteCtlConf.PKEY_PATH}")
    # uid = str(uuid4())
    # res = restore(host, uid='5aff518f-de1b-40af-820d-18f3899df715')

    # print(res)
    res = search_hosts('192.168.0.0/24')
    print(res)



if __name__ == "__main__":
    main()