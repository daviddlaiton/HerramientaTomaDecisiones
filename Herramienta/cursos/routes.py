from flask import render_template, abort, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from Herramienta.models import Usuario, Curso

cursos = Blueprint("cursos", __name__)

@cursos.route("/cursos")
@login_required
def get_cursos():
    user_id = current_user.get_id()
    user = Usuario.query.filter_by(id=user_id).first()
    if user.rol_id != 4:
        abort(403)
    cursos = Curso.query.all()
    return render_template("cursos.html", title="Cursos", cursos=cursos, usuario=user, showCursosSideBar=True)
