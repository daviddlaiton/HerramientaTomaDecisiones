from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from Herramienta.models import Usuario, Rol


class RegistrationForm(FlaskForm):
    login = StringField("Login", validators=[
                        DataRequired(), Length(min=2, max=20)])
    rol = SelectField("Tipo de usuario", choices=[], coerce=int)
    submit = SubmitField("Crear usuario")

class CrearMonitorForm(FlaskForm):
    login = StringField("Login", validators=[
                        DataRequired(), Length(min=2, max=20)])
    submit = SubmitField("Crear monitor")

class LoginForm(FlaskForm):
    login = StringField("Login", validators=[DataRequired()])
    password = PasswordField("Contraseña", validators=[DataRequired()])
    submit = SubmitField("Iniciar sesión")


class RequestResetForm(FlaskForm):
    login = StringField("Login", validators=[DataRequired()])
    submit = SubmitField("Solicitar cambio de contraseña")

class ResetPasswordForm(FlaskForm):
    password = PasswordField("Nueva contraseña", validators=[DataRequired()])
    confirm_password = PasswordField(" Confirmar contraseña", validators=[
                                     DataRequired(), EqualTo("password")])
    submit = SubmitField("Cambiar contraseña")

class EditarNombreUsuarioForm(FlaskForm):
    login = StringField("Usuario", validators=[
                        DataRequired(), Length(min=2, max=20)])
    submit = SubmitField("Editar usuario")

class EditarRolUsuarioForm(FlaskForm):
    rol = SelectField("Tipo de usuario", choices=[], coerce=int)
    submit = SubmitField("Editar usuario")

class AgregarCursoAUsuarioForm(FlaskForm) :
    curso = SelectField("Semestre a añadir", choices=[], coerce=int)
    submit = SubmitField("Agregar curso a usuario") 

class EliminarCursosAUsuarioForm(FlaskForm) :
    submit = SubmitField("Eliminar curso") 

class EliminarUsuarioForm(FlaskForm):
    submit = SubmitField("Eliminar usuario") 

class EliminarMonitorAsignadoForm(FlaskForm):
    submit = SubmitField("Eliminar monitor") 

class EstablecerContraseñaForm(FlaskForm):
    password = PasswordField("Contraseña", validators=[
                             DataRequired(), Length(min=6, max=50)])
    confirm_password = PasswordField(" Confirmar constraseña", validators=[
                                     DataRequired(), EqualTo("password")])
    submit = SubmitField("Establecer contraseña") 

class ActivarUsuarioForm(FlaskForm):
    nombres = StringField("Nombres ", validators=[DataRequired()])
    apellidos = StringField("Apellidos", validators=[DataRequired()])
    submit = SubmitField("Aceptar") 