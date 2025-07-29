from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db


class Host(db.Model):
    id: so.Mapped[int] = so.MappedColumn(primary_key=True)
    ip: so.Mapped[str] = so.MappedColumn(sa.String(15), unique=True)
    name: so.Mapped[str] = so.MappedColumn(sa.String(32), unique=True)

    def __repr__(self):
        return f"<Host {self.name} ip: {self.ip}>"
    
class Lab(db.Model):
    id: so.Mapped[int] = so.MappedColumn(primary_key=True)
    name: so.Mapped[str] = so.MappedColumn(sa.String(32), unique=True)
    

    def __repr__(self):
        return f"<Lab {self.name}>"

class Backup(db.Model):
    id: so.Mapped[int] = so.MappedColumn(primary_key=True)
    uuid: so.Mapped[str] = so.MappedColumn(sa.String(36), unique=True)
    comment: so.Mapped[str] = so.MappedColumn(sa.String(256), unique=True)
    host_id: so.Mapped[int] = so.MappedColumn(sa.ForeignKey(Host.id))
    dir: so.Mapped[str] = so.MappedColumn(sa.String(256), nullable=True)
    # host: so.WriteOnlyMapped['Host'] = so.relationship(back_populates='backups')
    lab_id: so.Mapped[int] = so.MappedColumn(sa.ForeignKey(Lab.id))
    # lab: so.WriteOnlyMapped['Lab'] = so.relationship(back_populates='backups')

    def __repr__(self):
        return f"<Backup {self.uuid}>"

# models will be here later
user = {
    "id": 1,
    "name": "Dmitry",
    "password": "123",
}

labs = {
    "1":{
        "name": "ЛР2.1 Администрирование межсетевых экранов",
        "manual_path": "manuals/ЛР2_1.pdf"    
    },
    "2": {
        "name": "ЛР2.2 Администрирование сетевых систем обнаружения вторжений",
        "manual_path": "manuals/ЛР2_2.pdf" 
    },
    "3": {
        "name": "ЛР2.3 Администрирование сетевых систем предотвращения вторжений",
        "manual_path": "manuals/ЛР2_3.pdf" 
    },
    "4":{
        "name": "ЛР3.1 Средства MTD для защиты компьютерных сетей",
        "manual_path": "manuals/ЛР3_1.pdf" 
    }
}

current_lab = {}
task_id = []

hosts = [{'id': "1",
          'ip': '10.0.0.10',
          'name': 'A1',
          }]

