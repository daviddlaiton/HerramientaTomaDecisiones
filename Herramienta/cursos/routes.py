from flask import render_template, url_for, flash, redirect, request, Blueprint, abort
from flask_login import current_user, login_required
from Herramienta.models import Usuario, Curso, Semestre
from Herramienta import db, bcrypt
from Herramienta.cursos.forms import CrearUsuarioForm, EditarNombreCursoForm, AgregarSemestreACursoForm, EliminarSemestreACursoForm, EliminarCursoForm

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
        semestres=[]
        curso = Curso(nombre=form.nombre.data,
                       semestres=semestres)
        db.session.add(curso)
        db.session.commit()
        flash(f"Curso creado exitosamente", "success")
        return redirect(url_for("cursos.get_cursos"))
    return render_template("cursos/crear_curso.html", title="Crear curso", form=form)

@cursos.route("/cursos/<int:curso_id>/editar", methods=["GET", "POST"])
@login_required
def editar_curso(curso_id):
    user_id = current_user.get_id()
    user = Usuario.query.filter_by(id=user_id).first()
    if user.rol_id == 1:
        abort(403)
    curso = Curso.query.get_or_404(curso_id)
    form = EditarNombreCursoForm()
    if form.validate_on_submit():
        curso.nombre = form.nombre.data
        db.session.commit()
        flash(f"Curso actualizado exitosamente", "success")
        return redirect(url_for("cursos.get_cursos"))
    elif request.method == "GET":
        form.nombre.data = curso.nombre
    return render_template("cursos/editar_curso.html", title="Editar curso", form=form)

@cursos.route("/cursos/<int:curso_id>", methods=["GET", "POST"])
@login_required
def ver_curso(curso_id):
    user_id = current_user.get_id()
    user = Usuario.query.filter_by(id=user_id).first()
    curso = Curso.query.get_or_404(curso_id)
    return render_template("cursos/ver_curso.html", title="Ver curso", curso=curso)

@cursos.route("/cursos/<int:curso_id>/editarNombre", methods=["GET", "POST"])
@login_required
def editarNombre_curso(curso_id):
    user_id = current_user.get_id()
    user = Usuario.query.filter_by(id=user_id).first()
    if user.rol_id == 1:
        abort(403)
    curso = Curso.query.get_or_404(curso_id)
    form = EditarNombreCursoForm()
    if form.validate_on_submit():
        curso.nombre = form.nombre.data
        db.session.commit()
        flash(f"Curso actualizado exitosamente", "success")
        return redirect(url_for("cursos.ver_curso", curso_id=curso.id))
    elif request.method == "GET":
        form.nombre.data = curso.nombre
    return render_template("cursos/editar_nombre_curso.html", title="Cambiar nombre curso", form=form, curso=curso)

@cursos.route("/cursos/<int:curso_id>/agregarSemestre", methods=["GET", "POST"])
@login_required
def agregarSemestre_curso(curso_id):
    user_id = current_user.get_id()
    user = Usuario.query.filter_by(id=user_id).first()
    if user.rol_id == 1:
        abort(403)
    curso = Curso.query.get_or_404(curso_id)
    semestresActuales = curso.semestres
    semestres = [(s.id, s.nombre)
              for s in Semestre.query.all() if s not in semestresActuales]
    form = AgregarSemestreACursoForm(request.form)
    form.semestre.choices = semestres
    if form.validate_on_submit():
        semestreAnadir = Semestre.query.filter_by(id=form.semestre.data).first()
        curso.semestres.append(semestreAnadir)
        db.session.commit()
        flash(f"Semestre añadido exitosamente", "success")
        return redirect(url_for("cursos.ver_curso", curso_id=curso.id))
    return render_template("cursos/anadirSemestre_curso.html", title="Anadir semestre a curso", form=form, curso=curso, semestres=semestres)


@cursos.route("/cursos/<int:curso_id>/eliminarSemestre/<int:semestre_id>", methods=["GET", "POST"])
@login_required
def eliminarCurso_semestre(semestre_id, curso_id):
    user_id = current_user.get_id()
    user = Usuario.query.filter_by(id=user_id).first()
    if user.rol_id == 1:
        abort(403)
    semestre = Semestre.query.get_or_404(semestre_id)
    curso = Curso.query.get_or_404(curso_id)
    form = EliminarSemestreACursoForm()
    if form.validate_on_submit():
        curso.semestres.remove(semestre)
        db.session.commit()
        flash(f"Semestre eliminado exitosamente", "success")
        return redirect(url_for("cursos.ver_curso", curso_id=curso.id))
    return render_template("cursos/eliminarSemestre_curso.html", title="Eliminar semestre a curso", form=form, semestre=semestre, curso=curso)


@cursos.route("/cursos/<int:curso_id>/eliminarCurso", methods=["GET", "POST"])
@login_required
def eliminar_curso(curso_id):
    user_id = current_user.get_id()
    user = Usuario.query.filter_by(id=user_id).first()
    if user.rol_id == 1:
        abort(403)
    curso = Curso.query.get_or_404(curso_id)
    form = EliminarCursoForm()
    if form.validate_on_submit():
        db.session.delete(curso)
        db.session.commit()
        flash(f"Curso eliminado exitosamente", "success")
        return redirect(url_for("cursos.get_cursos"))
    return render_template("cursos/eliminar_curso.html", title="Eliminar curso", form=form, curso=curso)
