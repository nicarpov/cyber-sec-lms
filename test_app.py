from app.remote_control import backup


# {"backup_id": uid,
#             "host": host,
#             "backup_cmd": backup_cmd,
#             "path": path,
#             "comment": comment,
#             }

host = '1.1.1.1'
comment = 'test comment'
backup_dir = '/backup'
link = "/backup/0/"

def test_backup_full():

    res = backup(host, comment, backup_dir)
    assert res['backup_id'] == "1"
    assert res['host'] == host
    assert res['backup_cmd'] == "rsync -aAXv --rsync-path='mkdir /backup/1/' --progress --exclude={'/backup/*','/dev/*','/proc/*','/sys/*','/tmp/*','/run/*','/mnt/*','/media/*','/lost+found'} / /backup/1/"
    assert res['comment'] == comment
    assert res['link_path'] == ""

def test_backup_linked():

    res = backup(host, comment, backup_dir, link_path=link)

    assert res['backup_id'] == "1"
    assert res['host'] == host
    assert res['backup_cmd'] == "rsync -aAXv --rsync-path='mkdir /backup/1/' --progress --exclude={'/backup/*','/dev/*','/proc/*','/sys/*','/tmp/*','/run/*','/mnt/*','/media/*','/lost+found'} --link-dest=/backup/0/ / /backup/1/"
    assert res['comment'] == comment
    assert res['link_path'] == link
