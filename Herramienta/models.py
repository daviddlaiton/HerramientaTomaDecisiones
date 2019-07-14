from datetime import datetime
from Herramienta import db, login_manager
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app


@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


class Rol(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), primary_key=True)
    usuarios = db.relationship("Usuario", backref="rol")

    def __repr__(self):
        return f"User('{self.name}')"


class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    rol_id = db.Column(db.Integer, db.ForeignKey("rol.id"), nullable=False)
    grupos = db.relationship("Grupo", backref="Calificador")

    def get_reset_token(self, expired_sec=1800):
        s = Serializer(current_app.config["SECRET_KEY"], expired_sec)
        return s.dumps({"user_id": self.id}).decode("utf-8")

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            user_id = s.loads(token)["user_id"]
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.login}')"


class Estudiante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.Integer, nullable=False, unique=True)
    login = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    magistral = db.Column(db.String(50), nullable=False)
    complementaria = db.Column(db.String(50), nullable=False)
    semestre_id = db.Column(db.Integer, db.ForeignKey(
        "semestre.id"), nullable=False)

    def __repr__(self):
        return f"User('{self.login}')"


class Curso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    semestre_id = db.Column(db.Integer, db.ForeignKey(
        "semestre.id"), nullable=False)
    usuarios = db.relationship("Usuario", backref="curso")


class Semestre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    profesores = db.Column(db.String(50), nullable=False)
    asistentes = db.Column(db.String(50), nullable=False)
    cursos = db.relationship("Curso", backref="Semestre")
    lista = db.relationship("Estudiante", backref="lista")


class Calificacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)


class Grupo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer, unique=True, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey(
        "Usuario.id"), nullable=False)


class Actividad(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    # Integrantes no debería ir dentro de grupo?
    porcentaje = db.Column(db.Integer, nullable=False)
    habilitada = db.Column(db.Boolean, nullable=False)


class Punto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    puntajePosible = db.Column(db.Float, nullable=False)


class Inciso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    puntajePosible = db.Column(db.Float, nullable=False)


class Criterio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    puntajePosible = db.Column(db.Float, nullable=False)


class subcriterio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    minimoPuntaje = db.Column(db.Float, nullable=False)
    maximoPuntaje = db.Column(db.Float, nullable=False)

class Variacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    esOtro = db.Column(db.Boolean, nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    maximoVeces =  db.Column(db.Integer, nullable=False)
    puntaje = db.Column(db.Float, nullable=False)
    esPenalizacion = db.Column(db.Boolean, nullable=False)
