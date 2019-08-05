from flask import render_template, url_for, flash, redirect, request, Blueprint, abort
from flask_login import current_user, login_required
from Herramienta.models import Usuario, Semestre, Curso
from Herramienta import db, bcrypt
from Herramienta.semestres.forms import (CrearSemestreForm, EditarNombreSemestreForm,
                                         AgregarCursoASemestreForm, EliminarCursoASemestreForm, EliminarSemestreForm)

semestres = Blueprint("semestres", __name__)


@semestres.route("/semestres")
@login_required
def get_semestres():
    page = request.args.get("page", 1, type=int)
    semestres = Semestre.query.order_by(
        Semestre.id.desc()).paginate(page=page, per_page=5)
    return render_template("semestres/semestres.html", title="Semestres", semestres=semestres)


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


@semestres.route("/semestres/<int:semestre_id>", methods=["GET", "POST"])
@login_required
def ver_semestre(semestre_id):
    user_id = current_user.get_id()
    user = Usuario.query.filter_by(id=user_id).first()
    if user.rol_id == 1:
        abort(403)
    semestre = Semestre.query.get_or_404(semestre_id)
    return render_template("semestres/ver_semestre.html", title="Editar semestre", semestre=semestre)


@semestres.route("/semestres/<int:semestre_id>/editarNombre", methods=["GET", "POST"])
@login_required
def editarNombre_semestre(semestre_id):
    user_id = current_user.get_id()
    user = Usuario.query.filter_by(id=user_id).first()
    if user.rol_id == 1:
        abort(403)
    semestre = Semestre.query.get_or_404(semestre_id)
    form = EditarNombreSemestreForm()
    if form.validate_on_submit():
        semestre.nombre = form.nombre.data
        db.session.commit()
        flash(f"Semestre actualizado exitosamente", "success")
        return redirect(url_for("semestre.ver_semestre"))
    elif request.method == "GET":
        form.nombre.data = semestre.nombre
    return render_template("semestres/editar_nombre_semestre.html", title="Cambiar nombre semestre", form=form, semestre=semestre)


@semestres.route("/semestres/<int:semestre_id>/agregarCurso", methods=["GET", "POST"])
@login_required
def agregarCurso_semestre(semestre_id):
    user_id = current_user.get_id()
    user = Usuario.query.filter_by(id=user_id).first()
    if user.rol_id == 1:
        abort(403)
    semestre = Semestre.query.get_or_404(semestre_id)
    cursosActuales = semestre.cursos
    cursos = [(c.id, c.nombre)
              for c in Curso.query.all() if c not in cursosActuales]
    form = AgregarCursoASemestreForm(request.form)
    form.curso.choices = cursos
    if form.validate_on_submit():
        cursoAnadir = Curso.query.filter_by(id=form.curso.data).first()
        semestre.cursos.append(cursoAnadir)
        db.session.commit()
        flash(f"Curso añadido exitosamente", "success")
        return redirect(url_for("semestres.ver_semestre", semestre_id=semestre.id))
    return render_template("semestres/anadirCurso_semestre.html", title="Anadir curso a semestre", form=form, semestre=semestre, cursos=cursos)


@semestres.route("/semestres/<int:semestre_id>/eliminarCurso/<int:curso_id>", methods=["GET", "POST"])
@login_required
def eliminarCurso_semestre(semestre_id, curso_id):
    user_id = current_user.get_id()
    user = Usuario.query.filter_by(id=user_id).first()
    if user.rol_id == 1:
        abort(403)
    semestre = Semestre.query.get_or_404(semestre_id)
    curso = Curso.query.get_or_404(curso_id)
    form = EliminarCursoASemestreForm()
    if form.validate_on_submit():
        semestre.cursos.remove(curso)
        db.session.commit()
        flash(f"Curso eliminado exitosamente", "success")
        return redirect(url_for("semestres.ver_semestre", semestre_id=semestre.id))
    return render_template("semestres/eliminarCurso_semestre.html", title="Eliminar curso a semestre", form=form, semestre=semestre, curso=curso)


@semestres.route("/semestres/<int:semestre_id>/eliminarSemestre", methods=["GET", "POST"])
@login_required
def eliminar_semestre(semestre_id):
    user_id = current_user.get_id()
    user = Usuario.query.filter_by(id=user_id).first()
    if user.rol_id == 1:
        abort(403)
    semestre = Semestre.query.get_or_404(semestre_id)
    form = EliminarSemestreForm()
    if form.validate_on_submit():
        db.session.delete(semestre)
        db.session.commit()
        flash(f"Semestre eliminado exitosamente", "success")
        return redirect(url_for("semestres.get_semestres"))
    return render_template("semestres/eliminar_semestre.html", title="Eliminar semestre", form=form, semestre=semestre)
