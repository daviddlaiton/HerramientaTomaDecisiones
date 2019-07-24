from flask import Flask
from Herramienta import db, bcrypt
from Herramienta.models import Usuario, Rol, Curso

def initial_insert():
    rol_1 = Rol(id=1,nombre="Monitor")
    rol_2 = Rol(id=2,nombre="Asistente")
    rol_3 = Rol(id=3,nombre="Profesor")
    rol_4 = Rol(id=4,nombre="Administrador")

    db.session.add(rol_1)
    db.session.add(rol_2)
    db.session.add(rol_3)
    db.session.add(rol_4)

    #curso_1 = Curso(id=1, nombre="Prueba")
    #db.session.add(curso_1)

    hashed_password = bcrypt.generate_password_hash("admin1").decode("utf-8")
    user = Usuario(login="admin", password=hashed_password, rol_id= 4)
    db.session.add(user)
    db.session.commit()