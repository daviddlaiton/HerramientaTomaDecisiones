from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from Herramienta.models import Curso

class CrearActividadArchivoForm(FlaskForm):
    archivo = FileField(u'Archivo de Excel', validators=[FileAllowed(['xls', 'xlsx'])])
    submit = SubmitField("Crear actividad")

class EliminarActividad(FlaskForm) :
    submit = SubmitField("Eliminar actividad") 