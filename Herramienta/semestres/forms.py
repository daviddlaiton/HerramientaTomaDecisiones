from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, ValidationError, NumberRange
from flask_login import current_user
from Herramienta.models import Semestre, Estudiante


class CrearSemestreForm(FlaskForm):
    nombre = StringField("Nombre", validators=[
                        DataRequired(), Length(min=1, max=50)])
    submit = SubmitField("Crear semestre")

    def validate_nombre(self, nombre):
        user = Semestre.query.filter_by(nombre=nombre.data).first()
        if user:
            raise ValidationError("Semestre ya existente")

class EditarNombreSemestreForm(FlaskForm):
    nombre = StringField("Nombre", validators=[
                        DataRequired(), Length(min=1, max=50)])
    submit = SubmitField("Cambiar nombre")

    def validate_nombre(self, nombre):
        user = Semestre.query.filter_by(nombre=nombre.data).first()
        if user:
            raise ValidationError("Semestre ya existente")

class AgregarCursoASemestreForm(FlaskForm) :
    curso = SelectField("Curso a añadir", choices=[], coerce=int)
    submit = SubmitField("Agregar curso a semestre") 

class EliminarCursoASemestreForm(FlaskForm) :
    submit = SubmitField("Eliminar curso") 

class EliminarSemestreForm(FlaskForm) :
    submit = SubmitField("Eliminar semestre") 

class CrearEstudianteForm(FlaskForm):
    login = StringField("Login", validators=[
                        DataRequired(), Length(min=2, max=20)])
    codigo = IntegerField("Código", validators=[
                        DataRequired()])
    nombres = StringField("Nombres", validators=[
                        DataRequired(), Length(min=2, max=50)])
    apellidos = StringField("Apellidos", validators=[
                        DataRequired(), Length(min=2, max=50)])
    magistral = StringField("Magistral", validators=[
                        DataRequired(), Length(min=1, max=50)])
    complementaria = StringField("Complementaria", validators=[
                        DataRequired(), Length(min=1, max=50)])
    submit = SubmitField("Crear usuario")

    def validate_login(self, login):
        estudiante = Estudiante.query.filter_by(login=login.data).first()
        if estudiante:
            raise ValidationError("Usuario con el login ingresado ya existe en el sistema.")

    def validate_codigo(self, codigo):
        estudiante = Estudiante.query.filter_by(codigo=codigo.data).first()
        if estudiante:
            raise ValidationError("Usuario con el código ingresado ya existe en el sistema.")

class AgregarEstudianteExistenteASemestreForm(FlaskForm) :
    login = SelectField("Login de estudiante a añadir", choices=[], coerce=int)
    submit = SubmitField("Agregar estudiante a semestre") 