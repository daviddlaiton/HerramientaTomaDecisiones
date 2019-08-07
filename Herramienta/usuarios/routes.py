from flask import render_template, url_for, flash, redirect, request, Blueprint, abort
from flask_login import login_user, current_user, logout_user, login_required
from Herramienta import db, bcrypt
from Herramienta.models import Usuario, Rol, Curso
from Herramienta.usuarios.forms import (RegistrationForm, LoginForm, RequestResetForm, ResetPasswordForm,
                                        EditarNombreUsuarioForm, EditarRolUsuarioForm, AgregarCursoAUsuarioForm, EliminarCursosAUsuarioForm,
                                        EliminarUsuarioForm)

usuarios = Blueprint("usuarios", __name__)


@usuarios.route("/register", methods=["GET", "POST"])
@login_required
def register():
    user_id = current_user.get_id()
    user = Usuario.query.filter_by(id=user_id).first()
    if user.rol_id != 4:
        abort(403)
    roles = [(r.id, r.nombre) for r in Rol.query.all()]
    form = RegistrationForm(request.form)
    form.rol.choices = roles
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode("utf-8")
        user = Usuario(login=form.login.data,
                       password=hashed_password, rol_id=form.rol.data)
        db.session.add(user)
        db.session.commit()
        flash(f"Usuario creado exitosamente", "success")
        return redirect(url_for("usuarios.get_usuarios"))
    return render_template("usuarios/crear_usuario.html", title="Crear usuario", form=form)


@usuarios.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = Usuario.query.filter_by(login=form.login.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("cursos.get_cursos"))
        else:
            flash("Login o contraseña invalidos.", "danger")
    return render_template("usuarios/login.html", title="Iniciar sesión", form=form)


@usuarios.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.home"))


@usuarios.route("/usuarios", methods=["GET", "POST"])
@login_required
def get_usuarios():
    user_id = current_user.get_id()
    user = Usuario.query.filter_by(id=user_id).first()
    if user.rol_id != 4:
        abort(403)
    page = request.args.get("page", 1, type=int)
    usuarios = Usuario.query.order_by(
        Usuario.id.desc()).paginate(page=page, per_page=5)
    return render_template("usuarios/usuarios.html", title="Usuarios", usuarios=usuarios, usuario=user)


@usuarios.route("/cuenta", methods=["GET", "POST"])
@login_required
def cuenta():
    user_id = current_user.get_id()
    user = Usuario.query.filter_by(id=user_id).first()
    rol = Rol.query.filter_by(id=user.rol_id).first()
    return render_template("usuarios/cuenta.html", title="Mi cuenta", usuario=user, rol=rol)


@usuarios.route("/usuarios/<int:usuario_id>/editarNombre", methods=["GET", "POST"])
@login_required
def editarNombre_usuario(usuario_id):
    user_id = current_user.get_id()
    user = Usuario.query.filter_by(id=user_id).first()
    if user.rol_id != 4:
        abort(403)
    usuario = Usuario.query.get_or_404(usuario_id)
    form = EditarNombreUsuarioForm()
    if form.validate_on_submit():
        usuario.login = form.login.data
        db.session.commit()
        flash(f"Usuario actualizado exitosamente", "success")
        return redirect(url_for("usuarios.ver_usuario", usuario_id=usuario.id))
    elif request.method == "GET":
        form.login.data = usuario.login
    return render_template("usuarios/editarNombre_usuario.html", title="Editar usuario", form=form)

@usuarios.route("/usuarios/<int:usuario_id>/editarRol", methods=["GET", "POST"])
@login_required
def editarRol_usuario(usuario_id):
    user_id = current_user.get_id()
    user = Usuario.query.filter_by(id=user_id).first()
    if user.rol_id != 4:
        abort(403)
    usuario = Usuario.query.get_or_404(usuario_id)
    roles = [(r.id, r.nombre) for r in Rol.query.all()]
    form = EditarRolUsuarioForm(request.form)
    form.rol.choices = roles
    if form.validate_on_submit():
        usuario.rol_id = form.rol.data
        db.session.commit()
        flash(f"Usuario actualizado exitosamente", "success")
        return redirect(url_for("usuarios.ver_usuario", usuario_id=usuario.id))
    return render_template("usuarios/editarRol_usuario.html", title="Editar usuario", form=form)

@usuarios.route("/usuarios/<int:usuario_id>", methods=["GET", "POST"])
@login_required
def ver_usuario(usuario_id):
    user_id = current_user.get_id()
    user = Usuario.query.filter_by(id=user_id).first()
    if user.rol_id != 4:
        abort(403)
    usuario = Usuario.query.get_or_404(usuario_id)
    return render_template("usuarios/ver_usuario.html", title="Ver usuario", usuario=usuario)


@usuarios.route("/usuarios/<int:usuario_id>/agregarCurso", methods=["GET", "POST"])
@login_required
def agregarCurso_usuario(usuario_id):
    user_id = current_user.get_id()
    user = Usuario.query.filter_by(id=user_id).first()
    if user.rol_id == 1:
        abort(403)
    usuario = Usuario.query.get_or_404(usuario_id)
    cursosActuales = usuario.cursos
    cursos = [(c.id, c.nombre)
              for c in Curso.query.all() if c not in cursosActuales]
    form = AgregarCursoAUsuarioForm(request.form)
    form.curso.choices = cursos
    if form.validate_on_submit():
        cursoAnadir = Curso.query.filter_by(
            id=form.curso.data).first()
        usuario.cursos.append(cursoAnadir)
        db.session.commit()
        flash(f"Curso añadido exitosamente", "success")
        return redirect(url_for("usuario.ver_usuario", usuario_id=usuario.id))
    return render_template("usuario/anadirCurso_usuario.html", title="Anadir cursos a usuario", form=form, usuario=usuario, cursos=cursos)


@usuarios.route("/usuarios/<int:usuario_id>/eliminarCurso/<int:curso_id>", methods=["GET", "POST"])
@login_required
def eliminarCurso_usuario(usuario_id, curso_id):
    user_id = current_user.get_id()
    user = Usuario.query.filter_by(id=user_id).first()
    if user.rol_id == 1:
        abort(403)
    usuario = Usuario.query.get_or_404(usuario_id)
    curso = Curso.query.get_or_404(curso_id)
    form = EliminarCursosAUsuarioForm()
    if form.validate_on_submit():
        usuario.semestres.remove(curso)
        db.session.commit()
        flash(f"Curso eliminado exitosamente", "success")
        return redirect(url_for("usuarios.ver_usuario", usuario_id=usuario.id))
    return render_template("usuarios/eliminarCurso_usuario.html", title="Eliminar curso a usuario", form=form, usuario=usuario, curso=curso)


@usuarios.route("/usuarios/<int:usuario_id>/eliminarUsuario", methods=["GET", "POST"])
@login_required
def eliminar_usuario(curso_id):
    user_id = current_user.get_id()
    user = Usuario.query.filter_by(id=user_id).first()
    if user.rol_id == 1:
        abort(403)
    usuario = Usuario.query.get_or_404(curso_id)
    form = EliminarUsuarioForm()
    if form.validate_on_submit():
        db.session.delete(usuario)
        db.session.commit()
        flash(f"Usuario eliminado exitosamente", "success")
        return redirect(url_for("usuarios.get_usuarios"))
    return render_template("usuarios/eliminar_usuario.html", title="Eliminar usuario", form=form, usuario=usuario)
