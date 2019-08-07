from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from Herramienta.models import Curso


class CrearUsuarioForm(FlaskForm):
    nombre = StringField("Nombre", validators=[
                        DataRequired(), Length(min=1, max=70)])
    submit = SubmitField("Crear curso")

    def validate_nombre(self, nombre):
        user = Curso.query.filter_by(nombre=nombre.data).first()
        if user:
            raise ValidationError("Curso ya existente")

class EditarNombreCursoForm(FlaskForm):
    nombre = StringField("Nombre", validators=[
                        DataRequired(), Length(min=1, max=70)])
    submit = SubmitField("Cambiar nombre curso")

    def validate_nombre(self, nombre):
        user = Curso.query.filter_by(nombre=nombre.data).first()
        if user:
            raise ValidationError("Curso ya existente")

class AgregarSemestreACursoForm(FlaskForm) :
    semestre = SelectField("Semestre a añadir", choices=[], coerce=int)
    submit = SubmitField("Agregar semestre a curso") 

class EliminarSemestreACursoForm(FlaskForm) :
    submit = SubmitField("Eliminar semestre") 

class EliminarCursoForm(FlaskForm) :
    submit = SubmitField("Eliminar curso") 
