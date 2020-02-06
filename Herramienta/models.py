import json
from json import JSONEncoder
from datetime import datetime
from Herramienta import db, login_manager
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app


@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


grupos = db.Table("integrantes",
                  db.Column("Grupo_id", db.Integer, db.ForeignKey(
                      "grupo.id"), primary_key=True),
                  db.Column("Estudiante_id", db.Integer, db.ForeignKey(
                      "estudiante.id"), primary_key=True)
                  )

cursos = db.Table("cursos",
                  db.Column("usuario_id", db.Integer, db.ForeignKey(
                      "usuario.id"), primary_key=True),
                  db.Column("curso_id", db.Integer, db.ForeignKey(
                      "curso.id"), primary_key=True)
                  )

semestres = db.Table("semestres",
                     db.Column("semestre_id", db.Integer, db.ForeignKey(
                         "semestre.id"), primary_key=True),
                     db.Column("curso_id", db.Integer, db.ForeignKey(
                         "curso.id"), primary_key=True)
                     )


class Rol(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), primary_key=True)
    usuarios = db.relationship("Usuario", backref="rol")

    def __repr__(self):
        return f"Rol('{self.nombre}','{self.id}')"


class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    nombres = db.Column(db.String(50))
    apellidos = db.Column(db.String(50))
    rol_id = db.Column(db.Integer, db.ForeignKey("rol.id"), nullable=False)
    grupos = db.relationship("Grupo", backref="Calificador")
    cursos = db.relationship("Curso", secondary=cursos, lazy="subquery",
                             backref=db.backref("usuarios", lazy=True))
    activado = db.Column(db.Boolean, nullable=False)

    def get_token_password(self, expired_sec=172800):
        s = Serializer(current_app.config["SECRET_KEY"], expired_sec)
        return s.dumps({"usuario_id": self.id}).decode("utf-8")

    @staticmethod
    def verify_token_password(token):
        s = Serializer(current_app.config["SECRET_KEY"])
        try:
            user_id = s.loads(token)["usuario_id"]
        except:
            return None
        return Usuario.query.get(user_id)

    def __repr__(self):
        return f"Usuario('{self.login}','{self.rol_id}', activado: '{self.activado}', nombres: '{self.nombres}')"

class ListaUsuariosSemestreCurso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    semestre_id = db.Column(db.Integer, db.ForeignKey(
        "semestre.id"), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey(
        "curso.id"), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey(
        "usuario.id"))
    
class SemestreCursoHabilitados(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    semestre_id = db.Column(db.Integer, db.ForeignKey(
        "semestre.id"), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey(
        "curso.id"), nullable=False)
    habilitado = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"'{self.semestre_id}' '{self.curso_id}' '{self.habilitado}'"


class Estudiante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.Integer, nullable=False)
    login = db.Column(db.String(20), nullable=False)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    magistral = db.Column(db.String(50), nullable=False)
    complementaria = db.Column(db.String(50), nullable=False)
    grupos = db.relationship("Grupo", secondary=grupos, lazy="subquery",
                             backref=db.backref("estudiantes", lazy=True))
    semestre = db.Column(db.Integer, db.ForeignKey(
        "semestre.id"), nullable=False)

    def __repr__(self):
        return f"'{self.nombre}' '{self.apellido}'"


class Curso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(70), nullable=False)
    semestres = db.relationship("Semestre", secondary=semestres, lazy="subquery",
        backref=db.backref("cursos", lazy=True))
    actividades = db.relationship("Actividad", backref="actividad")

    def __repr__(self):
        return f"Curso('{self.nombre}')"


class Semestre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    # Creo que debe ser una relación (profesores y asistentes)
    # profesores = db.Column(db.String(50), nullable=False)
    # asistentes = db.Column(db.String(50), nullable=False)
    estudiantes = db.relationship("Estudiante", backref="rol")
    actividades = db.relationship("Actividad", backref="semestre")

    def __repr__(self):
        return f"Semestre('{self.nombre}', '{self.id}'), Actividades('{self.actividades}', Estudiantes('{self.estudiantes}')) "


class Calificacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cantidadVeces = db.Column(db.Integer, nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    puntaje = db.Column(db.Float, nullable=False)
    grupo_id = db.Column(db.Integer, db.ForeignKey(
        "grupo.id"), nullable=False)
    # supongo que una calificacion puede tener más de 1 variación
    variacion_id = db.Column(db.Integer, db.ForeignKey(
        "variacion.id"), nullable=False)


class Grupo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey(
        "usuario.id"))
    creador = db.Column(db.String(20), unique=True, nullable=False)
    actividad_id = db.Column(db.Integer, db.ForeignKey(
        "actividad.id"), nullable=False)
    calificaciones = db.relationship("Calificacion", backref="grupos")
    calificado =  db.Column(db.Boolean, nullable=False)
    
    def __repr__(self):
        return f"Grupo('{self.id}'), Calificaciones('{self.calificaciones})', ) "

class Actividad(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numeroIntegrantes = db.Column(db.Integer, nullable=False) 
    nombre = db.Column(db.String(50), nullable=False)
    porcentaje = db.Column(db.Integer, nullable=False)
    habilitada = db.Column(db.Boolean, nullable=False)
    semestre_id = db.Column(db.Integer, db.ForeignKey(
        "semestre.id"), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey(
        "curso.id"), nullable=False)
    grupos = db.relationship("Grupo", backref="actividad")
    puntos = db.relationship("Punto", backref="actividad")
    numGrupos = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Actividad:'{self.nombre}':'{self.id}, habilitadad:'{self.habilitada}', Grupos: '{self.grupos}', Semestre:'{self.semestre_id}', Curso: '{self.curso_id}', Puntos:'{self.puntos}')"

class Punto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    puntajePosible = db.Column(db.Float, nullable=False)
    incisos = db.relationship("Inciso", backref="inciso")
    actividad_id = db.Column(db.Integer, db.ForeignKey(
        "actividad.id"), nullable=False)

    def __repr__(self):
        return f"Punto('{self.nombre}', '{self.incisos}')"


class Inciso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    puntajePosible = db.Column(db.Float, nullable=False)
    criterios = db.relationship("Criterio", backref="criterio")
    punto_id = db.Column(db.Integer, db.ForeignKey(
        "punto.id"), nullable=False)

    def __repr__(self):
            return f"Inciso('{self.nombre}', '{self.criterios}')"

class Criterio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    puntajePosible = db.Column(db.Float, nullable=False)
    subcriterios = db.relationship("Subcriterio", backref="subcriterio")
    inciso_id = db.Column(db.Integer, db.ForeignKey(
        "inciso.id"), nullable=False)


class Subcriterio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    minimoPuntaje = db.Column(db.Float, nullable=False)
    maximoPuntaje = db.Column(db.Float, nullable=False)
    variaciones = db.relationship("Variacion", backref="variacion")
    criterio_id = db.Column(db.Integer, db.ForeignKey(
        "criterio.id"), nullable=False)


class Variacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    esOtro = db.Column(db.Boolean, nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    maximoVeces = db.Column(db.Integer, nullable=False)
    puntaje = db.Column(db.Float, nullable=False)
    esPenalizacion = db.Column(db.Boolean, nullable=False)
    calificaciones = db.relationship("Calificacion", backref="calificacion")
    subcriterio_id = db.Column(db.Integer, db.ForeignKey(
        "subcriterio.id"), nullable=False)

    def __repr__(self):
        return f"Variacion('{self.descripcion}', '{self.puntaje}')"