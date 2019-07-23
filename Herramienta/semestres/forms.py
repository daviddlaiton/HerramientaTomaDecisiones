from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from Herramienta.models import Semestre


class CrearSemestreForm(FlaskForm):
    nombre = StringField("Nombre", validators=[
                        DataRequired(), Length(min=1, max=50)])
    submit = SubmitField("Crear semestre")

    def validate_nombre(self, nombre):
        user = Semestre.query.filter_by(nombre=nombre.data).first()
        if user:
            raise ValidationError("Semestre ya existente")
