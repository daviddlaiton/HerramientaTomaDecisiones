from flask import url_for, current_app
from flask_mail import Message
from Herramienta import mail
from fpdf import FPDF

def send_reset_email(user):
    token = user.get_token_password()
    user_mail = user.login + "@uniandes.edu.co"
    msg = Message(subject='Creación de contraseña',
                  sender='ad.laiton10@uniandes.edu.co',
                  recipients=[user_mail])
    msg.body = f'''Se ha creado un usuario en el OptiCorrector asociado a tu cuenta. Ingresa al siguiente link para poder establecer tu contraseña.:
{url_for('usuarios.reset_password', token=token, _external=True)}
Tienes 2 días desde la recepción de este correo para poder realizar esto. Pasado este tiempo es necesario que el admnistrador vuelva a crear tu usuario.
'''
    mail.send(msg)