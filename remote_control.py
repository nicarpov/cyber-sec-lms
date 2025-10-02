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
                        "key_filename": conf.PKEY_PATH,
                        },
            connect_timeout=30
        )



def backup(host, backup_uid: str, backup_dir: str = RemoteCtlConf.BACKUP_DIR, link_path: str = '/backup/base/', mocked: bool = True):
    """Makes backup of files in Linux-based system"""
    
    if backup_dir[-1] != '/':
        backup_dir = backup_dir + '/'
    path = os.path.join(backup_dir, backup_uid) + os.sep

    if platform == 'win32':
        path = Path(path).as_posix()
    if path[-1] != '/':
        path = path + '/'

    # if mocked:
    #     source = "/etc/netplan/"
    #     link_path = ""
    # else:
    source="/"
        
    link_option = " --link-dest={}"
    link_dest = link_option.format(link_path) if link_path else ''
    backup_cmd = "rsync -aAXv --rsync-path='mkdir {path}' --exclude={{'/home/remote/*','/home/user/*','{backup_dir}*','/dev/*','/proc/*','/sys/*','/tmp/*','/run/*','/mnt/*','/media/*','/lost+found'}}{link_dest} {source} {path}".format(backup_dir=backup_dir, path=path, link_dest=link_dest, source=source)
    
    try:
        with SSHConn(host=host) as conn:
            result = conn.sudo(backup_cmd, hide=True)
        # pass
    except Exception as err:
        return {"backup_id": backup_uid,
            "host": host,
            "backup_cmd": backup_cmd,
            "link_path": link_path or "",
            "path": path,
            "cmd_result": '',
            "err": repr(err),
            "cmd_code": 1
            }
    
    return {"backup_id": backup_uid,
            "host": host,
            "backup_cmd": backup_cmd,
            "link_path": link_path or "",
            "path": path
            # "cmd_error": result.stderr,
            # "cmd_code": result.exited
            }

def backup_routeros(host, backup_uid: str, backup_dir: str = RemoteCtlConf.BACKUP_DIR):
    """Makes backup of files in RouterOS-based system"""
    
    if backup_dir[-1] != '/':
        backup_dir = backup_dir + '/'
    path = os.path.join(backup_dir, backup_uid) + ".backup"
    
    backup_cmd = f"/system backup save name={backup_uid}.backup"
    with SSHConn('localhost', conf=RemoteCtlConf) as conn:
        try:
            res = conn.run(f'ssh {RemoteCtlConf.REMOTE_USER}@{host} {backup_cmd}', hide=True)
            conn.run(f"scp {RemoteCtlConf.REMOTE_USER}@{host}:{backup_uid}.backup /home/{RemoteCtlConf.REMOTE_USER}/{backup_uid}.backup")
            conn.sudo(f'mv /home/{RemoteCtlConf.REMOTE_USER}/{backup_uid}.backup {path}')
            return res.stdout
        except Exception as err:
            
            return {"backup_id": backup_uid,
            "host": host,
            "path": path,
            "err": repr(err)
           
            }
    
    return {"backup_id": backup_uid,
            "host": host,
            "path": path
            # "cmd_error": result.stderr,
            # "cmd_code": result.exited
            }

def restore_routeros(host, backup_uid: str, backup_dir: str = RemoteCtlConf.BACKUP_DIR):
    """Makes backup of files in RouterOS-based system"""
    
    if backup_dir[-1] != '/':
        backup_dir = backup_dir + '/'
    path = os.path.join(backup_dir, backup_uid) + ".backup"

    
    

    restore_cmd = f"/system backup load name={backup_uid}.backup password={RemoteCtlConf.REMOTE_PASS}"
    
    with SSHConn('localhost', conf=RemoteCtlConf) as conn:
        try:
            conn.sudo(f'cp {path} /home/{RemoteCtlConf.REMOTE_USER}/{backup_uid}.backup')
            conn.sudo(f'chown {RemoteCtlConf.REMOTE_USER} /home/{RemoteCtlConf.REMOTE_USER}/{backup_uid}.backup')
            conn.run(f"scp  /home/{RemoteCtlConf.REMOTE_USER}/{backup_uid}.backup {RemoteCtlConf.REMOTE_USER}@{host}:{backup_uid}.backup")
            res = conn.run(f'ssh {RemoteCtlConf.REMOTE_USER}@{host} "{restore_cmd}"', hide=True)
            conn.sudo(f'rm /home/{RemoteCtlConf.REMOTE_USER}/{backup_uid}.backup')
            
            
            return res.stdout
        except Exception as err:
            print("Error")
            return {
                "backup_id": backup_uid,
                "host": host,
                "path": path,
                "err": repr(err)
            }
    
    return {"backup_id": backup_uid,
            "host": host,
            "path": path
            # "cmd_error": result.stderr,
            # "cmd_code": result.exited
            }


def restore(host, backup_uid: str, backup_dir: str = RemoteCtlConf.BACKUP_DIR, autoreboot=False, mocked: bool = True, preset = []):
    
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
    dest = ""
    # if mocked:
    #     dest = "/home/"
    #     path = "/"
    # else:
    dest="/"
    print("Restore dest ", dest)
    restore_cmd = "rsync -aAXv --delete " \
                "--exclude={{'/home/student/snap/firefox/*','/usr/bin/firefox','/usr/bin/supervisorctl','/usr/bin/wireshark','/etc/supervisor/*','/etc/nginx/*','/etc/firefox/','/etc/wireshark/*','/home/remote/*','/home/user/*','{backup_dir}*','/dev/*','/proc/*','/sys/*','/tmp/*','/run/*','/mnt/*','/media/*','/lost+found'}} " \
                "{path} {dest}".format(path=path, backup_dir=backup_dir, dest=dest)
    
    result = {}
    with SSHConn(host=host) as conn:
        try:
            if preset:
                for cmd in preset:
                    conn.sudo(cmd, hide=True)
                    print("PRESET Cmd ", cmd, " executed")
            result = conn.sudo(restore_cmd, hide=True)
            if autoreboot:
                print("Autoreboot!!!")
                conn.sudo("shutdown -r +1", hide=True)
        except Exception as err:
            return {"backup_id": backup_uid,
                "host": host,
                "restore_cmd": restore_cmd,
                "path": path,
                "cmd_result": '',
                "err": repr(err),
                "cmd_code": 1
                }
        
    
    
    return {"backup_id": backup_uid,
            "host": host,
            "restore_cmd": restore_cmd,
            "path": path,
            "cmd_error": result.stderr,
            "cmd_code": result.exited,
            "preset": preset
            }
def routeros_backup_remove(backup_uid: str):
    
    return backup_remove('127.0.0.1',backup_uid)
    

def backup_remove(host, backup_uid: str, backup_dir: str = RemoteCtlConf.BACKUP_DIR):
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
    remove_cmd = "rm -rf {path}".format(path=path)
    
    try:
        with SSHConn(host=host) as conn:
            result = conn.sudo(remove_cmd, hide=True)
        
    except Exception as err:
        return {"backup_id": backup_uid,
            "host": host,
            "remove_cmd": remove_cmd,
            "path": path,
            "cmd_result": '',
            "err": repr(err),
            "cmd_code": 1
            }
    
    return {"backup_id": backup_uid,
            "host": host,
            "remove_cmd": remove_cmd,
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
    cmd = f"shutdown -r +1"
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
            "err": repr(err),
            "cmd_code": 1
            }
    
    return {
            "host": host,
            "cmd": cmd,
            "cmd_result": '',
            "cmd_code": 0
            }

def run_cmd_set(host, set):
    
    try:
        with SSHConn(host=host) as conn:
            # print('SSHConn', conn.config.sudo)
            cmd = ''
            for c in set:
                cmd = c
                conn.sudo(cmd, hide=True)
                
            # print('reboot res:', result)
        
    except Exception as err:
        return {
            "host": host,
            "cmd": cmd,
            "cmd_result": '',
            "err": repr(err),
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
        
def routeros_test():
    with SSHConn('localhost', conf=RemoteCtlConf) as conn:
        try:
            res = conn.run('ssh remote@192.168.1.13 "/ip address print"', hide=True)
            return res.stdout
        except Exception as err:
            print("Error")
            return err
    
def main():
    print(f"Connect using {RemoteCtlConf.PKEY_PATH}")
    # uid = str(uuid4())
    # res = restore(host, uid='5aff518f-de1b-40af-820d-18f3899df715')

    # print(res)
    # res = search_hosts('192.168.0.0/24')
    uid = 'c7b154e8-315c-456f-a7b8-6f1fb0434b44'
    # res = backup_routeros(host='192.168.1.13', backup_uid=uid)
    res = restore_routeros(host='192.168.1.13', backup_uid="c7b154e8-315c-456f-a7b8-6f1fb0434b44")
    print(res)



if __name__ == "__main__":
    main()
