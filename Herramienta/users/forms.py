from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from Herramienta.models import User

class RegistrationForm(FlaskForm):
    username = StringField("Usuario", validators=[DataRequired(),Length(min=2, max=20)])
    email = StringField("Correo", validators=[DataRequired(), Email()])
    password = PasswordField("Contraseña", validators=[DataRequired(),Length(min=6, max=50)])
    confirm_password = PasswordField(" Confirmar constraseña", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Registrarse")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Usuario ya existente en el sistema.") 

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Correo ya usado.") 

class LoginForm(FlaskForm):
    email = StringField("Correo", validators=[DataRequired(), Email()])
    password = PasswordField("Contraseña", validators=[DataRequired()])
    remember = BooleanField("Recuerdame")
    submit = SubmitField("Iniciar sesión")

class RequestResetForm(FlaskForm):
    email = StringField("Correo", validators=[DataRequired(), Email()])
    submit = SubmitField("Solicitar cambio de contraseña")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError("No existe una cuenta asignada a ese correo .") 

class ResetPasswordForm(FlaskForm):
    password = PasswordField("Nueva contraseña", validators=[DataRequired()])
    confirm_password = PasswordField(" Confirmar contraseña", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Cambiar contraseña")