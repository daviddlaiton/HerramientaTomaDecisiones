from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, IntegerField, FieldList, FormField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from Herramienta.models import Curso

class CrearActividadArchivoForm(FlaskForm):
    archivo = FileField(u'Archivo de Excel', validators=[FileAllowed(['xlsx'])])
    submit = SubmitField("Crear actividad")

class EliminarActividad(FlaskForm):
    submit = SubmitField("Eliminar actividad")

class EliminarGrupo(FlaskForm): 
    submit = SubmitField("Eliminar grupo")

class DescargarActividad(FlaskForm):
    submit = SubmitField("Descargar actividad") 

class CrearPunto(FlaskForm):
    nombre = StringField("Nombre del punto", validators=[
                        DataRequired(), Length(min=1, max=100)])
    submit = SubmitField("Crear punto")

class CambiarEstadoActividad(FlaskForm):
    submit = SubmitField("Cambiar estado")

class EnviarReportes(FlaskForm):
    submit = SubmitField("Enviar reportes")

class GenerarReporte(FlaskForm):
    submit = SubmitField("Generar informe")

class IntegranteForm(FlaskForm):
    codigo = SelectField("Código", choices=[], coerce=int)

class EscogerGrupoParaCalificar(FlaskForm):
    grupo = SelectField("Grupo", choices=[], coerce=int)
    submit = SubmitField("Seleccionar grupo para calificar")

class DescargarFormatoActividadForm(FlaskForm):
    submit = SubmitField("Descargar formato actividad") 