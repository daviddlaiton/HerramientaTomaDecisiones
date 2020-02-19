from flask import render_template, url_for, flash, redirect, request, Blueprint, abort
from flask_login import current_user, login_required
from Herramienta.models import Usuario, Curso, Semestre, Actividad, Grupo, SemestreCursoHabilitados, ListaUsuariosSemestreCurso, Calificacion
from Herramienta import db, bcrypt
from Herramienta.cursos.forms import CrearUsuarioForm, EditarNombreCursoForm, AgregarSemestreACursoForm, EliminarSemestreACursoForm, EliminarCursoForm

cursos = Blueprint("cursos", __name__)

@cursos.route("/cursos")
@login_required
def get_cursos():
    if not current_user.activado:
        return redirect(url_for("usuarios.activar_usuario"))
    user_id = current_user.get_id()
    user = Usuario.query.filter_by(id=user_id).first()
    listaCursos = ListaUsuariosSemestreCurso.query.filter_by(usuario_id=user_id).all()
    posiblesCursos = Curso.query.all()
    cursos = []
    if user.rol_id == 1:
        for curso in posiblesCursos:
            for cursoEnLista in listaCursos:
                if cursoEnLista.curso_id == curso.id:
                    cursos.append(curso)
    else:
        cursos = posiblesCursos
    return render_template("cursos/cursos.html", title="Cursos", cursos=cursos)

@cursos.route("/crear_curso", methods=["GET", "POST"])
@login_required
def crear_curso():
    if not current_user.activado:
        return redirect(url_for("usuarios.activar_usuario"))
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
    if not current_user.activado:
        return redirect(url_for("usuarios.activar_usuario"))
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
    if not current_user.activado:
        return redirect(url_for("usuarios.activar_usuario"))
    user_id = current_user.get_id()
    user = Usuario.query.filter_by(id=user_id).first()
    if user.rol_id == 1:
        habilitado = ListaUsuariosSemestreCurso.query.filter_by(usuario_id=user_id, curso_id=curso_id).first()
        if not habilitado:
            abort(403)
    curso = Curso.query.get_or_404(curso_id)
    listaSemestres = SemestreCursoHabilitados.query.filter_by(curso_id=curso_id).all()
    semestres = []
    numActividadesHabilitadasTotal = 0
    for s in listaSemestres:
        numActividadesHabilitadas = 0
        semestre = Semestre.query.get_or_404(s.semestre_id)
        listaActividades = Actividad.query.filter_by(semestre_id=s.semestre_id, curso_id=curso_id).all()
        for actividad in listaActividades:
            if actividad.habilitada:
                numActividadesHabilitadas = numActividadesHabilitadas + 1
                numActividadesHabilitadasTotal = numActividadesHabilitadasTotal +1
        listaUsuarios=ListaUsuariosSemestreCurso.query.filter_by(semestre_id=s.semestre_id, curso_id=curso_id).all()
        anadir = False
        if user.rol_id == 1:
            usuarioEnLista = ListaUsuariosSemestreCurso.query.filter_by(semestre_id=s.semestre_id, curso_id=curso_id, usuario_id=user_id).first()
            if usuarioEnLista is not None:
                anadir = True
        else:
            anadir = True
        if anadir:
            numUsuarios = len(listaUsuarios)
            semestreAnadir = {
                "id": semestre.id,
                "nombre" : semestre.nombre,
                "estudiantes" : semestre.estudiantes,
                "usuarios": numUsuarios,
                "actividades" : semestre.actividades,
                "habilitado" : s.habilitado,
                "actividadesHabilitadas" : numActividadesHabilitadas
            }
            semestres.append(semestreAnadir)
    return render_template("cursos/ver_curso.html", title="Ver curso", curso=curso, semestres=semestres, numActividadesHabilitadasTotal=numActividadesHabilitadasTotal)

@cursos.route("/cursos/<int:curso_id>/<int:semestre_id>/cambiarEstado", methods=["GET", "POST"])
@login_required
def cambiarEstadoSemestreCurso(curso_id,semestre_id):
    if not current_user.activado:
        return redirect(url_for("usuarios.activar_usuario"))
    elemento = SemestreCursoHabilitados.query.filter_by(semestre_id=semestre_id, curso_id=curso_id).first()
    elemento.habilitado = not elemento.habilitado
    db.session.commit()
    return redirect(url_for("cursos.ver_curso", curso_id=curso_id))

@cursos.route("/cursos/<int:curso_id>/editarNombre", methods=["GET", "POST"])
@login_required
def editarNombre_curso(curso_id):
    if not current_user.activado:
        return redirect(url_for("usuarios.activar_usuario"))
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
    if not current_user.activado:
        return redirect(url_for("usuarios.activar_usuario"))
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
        semestreCurso = SemestreCursoHabilitados(semestre_id=semestreAnadir.id,curso_id=curso_id,habilitado=True)
        db.session.add(semestreCurso)
        db.session.commit()
        flash(f"Semestre añadido exitosamente", "success")
        return redirect(url_for("cursos.ver_curso", curso_id=curso.id))
    return render_template("cursos/anadirSemestre_curso.html", title="Anadir semestre a curso", form=form, curso=curso, semestres=semestres)


@cursos.route("/cursos/<int:curso_id>/eliminarSemestre/<int:semestre_id>", methods=["GET", "POST"])
@login_required
def eliminarCurso_semestre(semestre_id, curso_id):
    if not current_user.activado:
        return redirect(url_for("usuarios.activar_usuario"))
    user_id = current_user.get_id()
    user = Usuario.query.filter_by(id=user_id).first()
    if user.rol_id == 1:
        abort(403)
    semestre = Semestre.query.get_or_404(semestre_id)
    curso = Curso.query.get_or_404(curso_id)
    form = EliminarSemestreACursoForm()
    if form.validate_on_submit():
        curso.semestres.remove(semestre)
        semestreCurso = SemestreCursoHabilitados.query.filter_by(semestre_id=semestre_id, curso_id=curso_id).first()
        db.session.delete(semestreCurso)
        db.session.commit()
        flash(f"Semestre eliminado exitosamente", "success")
        return redirect(url_for("cursos.ver_curso", curso_id=curso.id))
    return render_template("cursos/eliminarSemestre_curso.html", title="Eliminar semestre a curso", form=form, semestre=semestre, curso=curso)


@cursos.route("/cursos/<int:curso_id>/eliminarCurso", methods=["GET", "POST"])
@login_required
def eliminar_curso(curso_id):
    if not current_user.activado:
        return redirect(url_for("usuarios.activar_usuario"))
    user_id = current_user.get_id()
    user = Usuario.query.filter_by(id=user_id).first()
    if user.rol_id == 1:
        abort(403)
    curso = Curso.query.get_or_404(curso_id)
    actividades = Actividad.query.filter_by(curso_id=curso.id).all()
    form = EliminarCursoForm()
    if form.validate_on_submit():
        for actividad in actividades:
            grupos = Grupo.query.filter_by(actividad_id=actividad.id).all()
            for grupo in grupos:
                listaCalificaciones = Calificacion.query.filter_by(grupo_id=grupo.id).all()
                for calificacion in listaCalificaciones:
                    db.session.delete(calificacion)
                    db.session.commit()
                db.session.delete(grupo)
                db.session.commit()
            eliminarActividad(actividad.id)
            db.session.commit()
        for semestre in curso.semestres:
            curso.semestres.remove(semestre)
            semestreCurso = SemestreCursoHabilitados.query.filter_by(semestre_id=semestre.id, curso_id=curso_id).first()
            db.session.delete(semestreCurso)
            db.session.commit()
        db.session.delete(curso)
        db.session.commit()
        flash(f"Curso eliminado exitosamente", "success")
        return redirect(url_for("cursos.get_cursos"))
    return render_template("cursos/eliminar_curso.html", title="Eliminar curso", form=form, curso=curso)

def eliminarActividad(actividad_id):
    actividad = Actividad.query.get_or_404(actividad_id)

    for punto in actividad.puntos:
        #-------------------------------------------------------------------
        for inciso in punto.incisos:
            #-------------------------------------------------------------------
            for criterio in inciso.criterios:
                #-------------------------------------------------------------------
                for subcriterio in criterio.subcriterios:
                    #-------------------------------------------------------------------
                    for variacion in subcriterio.variaciones:
                        db.session.delete(variacion)
                        db.session.commit()
                    #-------------------------------------------------------------------
                    db.session.delete(subcriterio)
                    db.session.commit()
                #-------------------------------------------------------------------
                db.session.delete(criterio)
                db.session.commit()
            #-------------------------------------------------------------------
            db.session.delete(inciso)
            db.session.commit()
        #-------------------------------------------------------------------
        db.session.delete(punto)
        db.session.commit()
    
    db.session.delete(actividad)
    db.session.commit()