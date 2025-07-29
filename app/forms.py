from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from wtforms.validators import IPAddress, ValidationError, DataRequired
from app import db
from app.models import Host, Lab
import sqlalchemy as sa


class EmptyForm(FlaskForm):
    submit = SubmitField("Submit")


class HostCreate(FlaskForm):
    name = StringField('Имя хоста', validators=[DataRequired()])
    ip = StringField('IP-адрес хоста', validators=[IPAddress(), DataRequired()])

    submit = SubmitField('Зарегистрировать хост')

    def validate_name(self, name):
        query = sa.select(Host).where(Host.name == name.data)
        result = db.session.scalar(query)
        if result is not None:
            raise ValidationError('Имя уже зарегистрировано')
        
    def validate_ip(self, ip):
        query = sa.select(Host).where(Host.ip == ip.data)
        result = db.session.scalar(query)
        if result is not None:
            raise ValidationError('Адрес уже зарегистрирован')
        
class LabCreate(FlaskForm):
    name = StringField('Название лабораторной работы', validators=[DataRequired()])
    submit = SubmitField('Зарегистрировать хост')

    def validate_name(self, name):
        query = sa.select(Lab).where(Lab.name == name.data)
        result = db.session.scalar(query)
        if result is not None:
            raise ValidationError('Имя уже зарегистрировано')