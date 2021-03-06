from flask import render_template, Blueprint, redirect, url_for
from flask_login import current_user

main = Blueprint("main", __name__)

@main.route("/")
def home():
    if current_user.is_authenticated:
        if not current_user.activado:
            return redirect(url_for("usuarios.activar_usuario"))
        else:
            return redirect(url_for("cursos.get_cursos"))
    else: 
        return render_template("main/home.html", title="Inicio")
