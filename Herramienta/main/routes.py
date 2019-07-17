from flask import render_template, request, Blueprint
from flask_login import current_user
from Herramienta.models import Usuario

main = Blueprint("main", __name__)

@main.route("/")
@main.route("/home")
def home():
    id_usuario = current_user.get_id()
    usuario = Usuario.query.filter_by(id=id_usuario).first()
    return render_template("home.html", title="Inicio", usuario=usuario)
