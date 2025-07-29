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

    def validate_name(self):
        query = sa.select(Host).where(Host.name == self.name)
        result = db.session.scalars(query).all()
        if result is not None:
            raise ValidationError('Имя уже зарегистрировано')
        
    def validate_ip(self):
        query = sa.select(Host).where(Host.ip == self.ip)
        result = db.session.scalars(query).all()
        if result is not None:
            raise ValidationError('Адрес уже зарегистрирован')