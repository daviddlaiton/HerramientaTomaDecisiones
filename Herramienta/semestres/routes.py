from flask import render_template, url_for, flash, redirect, request, Blueprint, abort
from flask_login import current_user, login_required
from Herramienta.models import Usuario, Semestre
from Herramienta import db, bcrypt
from Herramienta.semestres.forms import CrearSemestreForm

semestres = Blueprint("semestres", __name__)

@semestres.route("/semestres")
@login_required
def get_semestres():
    page = request.args.get("page", 1, type=int)
    semestres = Semestre.query.order_by(Semestre.id.desc()).paginate(page=page, per_page=5)
    return render_template("semestres/semestres.html", title="Cursos", semestres=semestres)

@semestres.route("/crear_semestre", methods=["GET", "POST"])
@login_required
def crear_semestre():
    user_id = current_user.get_id()
    user = Usuario.query.filter_by(id=user_id).first()
    if user.rol_id == 1:
        abort(403)
    form = CrearSemestreForm()
    if form.validate_on_submit():
        semestre = Semestre(nombre=form.nombre.data)
        db.session.add(semestre)
        db.session.commit()
        flash(f"Semestre creado exitosamente", "success")
        return redirect(url_for("semestres.get_semestres"))
    return render_template("semestres/crear_semestre.html", title="Crear semestre", form=form)
