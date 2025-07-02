from app.remote_control import backup

def backup_test():
    host = '1.1.1.1'
    comment = 'test comment'
    backup_dir = '/backup'
    res = backup(host, comment, backup_dir)
    assert res['host'] == host
    assert res['comment'] == comment
