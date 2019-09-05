from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from Herramienta.config import Config

db = SQLAlchemy()
bcrypt = Bcrypt() 
login_manager = LoginManager()
login_manager.login_view = "users.login"
login_manager.login_message_category = "info"

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app) 
    bcrypt.init_app(app)
    login_manager.init_app(app) 

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