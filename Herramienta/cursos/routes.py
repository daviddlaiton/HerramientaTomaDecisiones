from flask import render_template, url_for, flash, redirect, request, Blueprint, abort
from flask_login import current_user, login_required
from Herramienta.models import Usuario, Curso
from Herramienta import db, bcrypt
from Herramienta.cursos.forms import CrearUsuarioForm

cursos = Blueprint("cursos", __name__)

@cursos.route("/cursos")
@login_required
def get_cursos():
    page = request.args.get("page", 1, type=int)
    cursos = Curso.query.order_by(Curso.id.desc()).paginate(page=page, per_page=5)
    return render_template("cursos/cursos.html", title="Cursos", cursos=cursos)

@cursos.route("/crear_curso", methods=["GET", "POST"])
@login_required
def crear_curso():
    user_id = current_user.get_id()
    user = Usuario.query.filter_by(id=user_id).first()
    if user.rol_id == 1:
        abort(403)
    form = CrearUsuarioForm()
    if form.validate_on_submit():
        semestre_id_int = int(form.semestre.data)
        semestres=[]
        semestres.append(semestre_id_int)
        curso = Curso(nombre=form.nombre.data,
                       semestre=semestres)
        db.session.add(curso)
        db.session.commit()
        flash(f"Cursos creado exitosamente", "success")
        return redirect(url_for("cursos.get_cursos"))
    return render_template("cursos/crear_curso.html", title="Crear curso", form=form)
