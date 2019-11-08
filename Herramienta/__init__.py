import flask_mail
from email.policy import EmailPolicy, SMTP
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from Herramienta.config import Config

# Headers that contain msg-id values, RFC5322
MSG_ID_HEADERS = {'message-id', 'in-reply-to', 'references', 'resent-msg-id'}

class MsgIdExcemptPolicy(EmailPolicy):
    def _fold(self, name, value, *args, **kwargs):
        if (name.lower() in MSG_ID_HEADERS and
            self.max_line_length < 998 and
            self.max_line_length - len(name) - 2 < len(value)
        ):
            # RFC 5322, section 2.1.1: "Each line of characters MUST be no
            # more than 998 characters, and SHOULD be no more than 78
            # characters, excluding the CRLF.". To avoid msg-id tokens from being folded
            # by means of RFC2047, fold identifier lines to the max length instead.
            return self.clone(max_line_length=998)._fold(name, value, *args, **kwargs)
        return super()._fold(name, value, *args, **kwargs)

flask_mail.message_policy = MsgIdExcemptPolicy() + SMTP

db = SQLAlchemy()
bcrypt = Bcrypt() 
login_manager = LoginManager()
login_manager.login_view = "users.login"
login_manager.login_message_category = "info"
mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app) 
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from Herramienta.main.routes import main 
    from Herramienta.usuarios.routes import usuarios 
    from Herramienta.errors.handlers import errors
    from Herramienta.cursos.routes import cursos
    from Herramienta.semestres.routes import semestres
    from Herramienta.actividades.routes import actividades

    app.register_blueprint(main)
    app.register_blueprint(usuarios)
    app.register_blueprint(errors)
    app.register_blueprint(cursos)
    app.register_blueprint(semestres)
    app.register_blueprint(actividades)
     
    return app