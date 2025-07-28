from app.remote_control import backup, restore, reboot
import dotenv
import os

dotenv.load_dotenv()

MOCKED=os.environ.get('MOCKED') or 1

# {"backup_id": uid,
#             "host": host,
#             "backup_cmd": backup_cmd,
#             "path": path,
#             "comment": comment,
#             }

host = '1.1.1.1'
uid='123'
comment = 'test comment'
backup_dir = '/backup'
link = "/backup/0/"

def test_backup_full():

    res = backup(host, uid=uid, comment=comment, backup_dir=backup_dir)
    assert res['backup_id'] == uid
    assert res['host'] == host
    assert res['backup_cmd'] == "rsync -aAXv --rsync-path='mkdir /backup/123/' --exclude={'/backup/*','/dev/*','/proc/*','/sys/*','/tmp/*','/run/*','/mnt/*','/media/*','/lost+found'} / /backup/123/"
    assert res['comment'] == comment
    assert res['link_path'] == ""

def test_backup_linked():

    res = backup(host, uid=uid, comment=comment, backup_dir=backup_dir, link_path=link)

    assert res['backup_id'] == "123"
    assert res['host'] == host
    assert res['backup_cmd'] == "rsync -aAXv --rsync-path='mkdir /backup/123/' --exclude={'/backup/*','/dev/*','/proc/*','/sys/*','/tmp/*','/run/*','/mnt/*','/media/*','/lost+found'} --link-dest=/backup/0/ / /backup/123/"
    assert res['comment'] == comment
    assert res['link_path'] == link

def test_restore():

    res = restore(host, uid=uid, backup_dir=backup_dir)
    assert res['backup_id'] == uid
    assert res['host'] == host
    assert res['backup_cmd'] == "rsync -aAXv --delete --exclude={'/backup/*','/dev/*','/proc/*','/sys/*','/tmp/*','/run/*','/mnt/*','/media/*','/lost+found'} /backup/123/ /"

def main():
    res = reboot('localhost')
    print(res)

if __name__ == "__main__":
    main()
    
    
