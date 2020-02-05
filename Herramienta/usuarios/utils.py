from flask import url_for, current_app
from flask_mail import Message
from Herramienta import mail
from fpdf import FPDF

def usuario_creado_email(user):
    token = user.get_token_password()
    user_mail = user.login + "@uniandes.edu.co"
    msg = Message(subject='Creación de contraseña',
                  sender='ad.laiton10@uniandes.edu.co',
                  recipients=[user_mail])
    msg.body = f'''Hola.

Se ha creado un usuario en el OptiCorrector asociado a tu cuenta. Ingresa al siguiente link para poder establecer tu contraseña.:

{url_for('usuarios.reset_password', token=token, _external=True)}

Tienes 2 días desde la recepción de este correo para poder realizar esto. Pasado este tiempo puedes utilizar el botón "¿Olvidaste tu contraseña?" presente en la página del Opticorrector.

Equipo Principios de Optimización.
'''
    mail.send(msg)

def send_reset_email(user):
    token = user.get_token_password()
    user_mail = user.login + "@uniandes.edu.co"
    msg = Message(subject='Cambio de contraseña',
                  sender='ad.laiton10@uniandes.edu.co',
                  recipients=[user_mail])
    msg.body = f'''Se ha solicitado un cambio de contraseña. Ingresa al siguiente link para poder establecer tu nueva contraseña.:
{url_for('usuarios.reset_password', token=token, _external=True)}
Tienes 2 días desde la recepción de este correo para poder realizar esto. Pasado este tiempo es necesario generar un nuevo link de cambio de contraseña.
'''
    mail.send(msg)