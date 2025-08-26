from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db
from datetime import datetime, timezone

class Host(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    ip: so.Mapped[str] = so.mapped_column(sa.String(15), unique=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(32), unique=True)
    os_type: so.Mapped[str] = so.mapped_column(sa.String(32), default='linux', nullable=True)
    backups: so.WriteOnlyMapped['Backup'] = so.relationship(back_populates='host', cascade='all, delete-orphan', passive_deletes=True)

    def __repr__(self):
        return f"<Host {self.name} ip: {self.ip}>"
    
class Lab(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(256), unique=True)
    saves: so.WriteOnlyMapped['Save'] = so.relationship(back_populates='lab', cascade='all, delete-orphan', passive_deletes=True)
    description: so.Mapped[str] = so.mapped_column(sa.String(1000), nullable=True)
    hidden: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False, nullable=True)

    def hide(self):
        self.hidden = True

    def show(self):
        self.hidden = False

    def __repr__(self):
        return f"<Lab {self.name}>"

class Save(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    uid: so.Mapped[str] = so.mapped_column(sa.String(36), unique=True)
    lab_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Lab.id, ondelete='CASCADE'))
    lab: so.Mapped[Lab] = so.relationship(back_populates='saves')
    backups: so.WriteOnlyMapped['Backup'] = so.relationship(back_populates='save', cascade='save-update, merge, delete', passive_deletes=True)
    comment: so.Mapped[str] = so.mapped_column(sa.String(256))
    is_default: so.Mapped[bool] = so.mapped_column(sa.Boolean(), default=False)
    timestamp: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc), nullable=True)

    def validate_default(self):
        default_save = db.session.scalar(sa.select(Save).where(Save.is_default == True))
        if default_save is None:
            self.is_default = True
            

    def set_default(self):
        default_save = db.session.scalar(sa.select(Save).where(Save.is_default == True))
        if default_save:
            default_save.is_default = False
        self.is_default = True

    def get_backups(self):
        return db.session.scalars(self.backups.select()).all()
        

class Backup(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    uid: so.Mapped[str] = so.mapped_column(sa.String(36), unique=True)
    comment: so.Mapped[str] = so.mapped_column(sa.String(256))
    host_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Host.id, ondelete='CASCADE'))
    dir: so.Mapped[str] = so.mapped_column(sa.String(256), nullable=True)
    host: so.Mapped[Host] = so.relationship(back_populates='backups')
    save_id: so.Mapped[int] = so.MappedColumn(sa.ForeignKey(Save.id, ondelete='CASCADE'))
    save: so.Mapped[Save] = so.relationship(back_populates='backups')

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

