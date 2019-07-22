from flask import render_template, abort, Blueprint, request
from flask_login import login_user, current_user, logout_user, login_required
from Herramienta.models import Usuario, Curso

cursos = Blueprint("cursos", __name__)

@cursos.route("/cursos")
@login_required
def get_cursos():
    page = request.args.get("page", 1, type=int)
    cursos = Curso.query.order_by(Curso.id.desc()).paginate(page=page, per_page=10)
    print(cursos)
    return render_template("cursos/cursos.html", title="Cursos", cursos=cursos)
