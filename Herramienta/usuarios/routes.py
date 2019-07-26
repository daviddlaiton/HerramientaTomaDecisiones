from flask import render_template, url_for, flash, redirect, request, Blueprint, abort
from flask_login import login_user, current_user, logout_user, login_required
from Herramienta import db, bcrypt
from Herramienta.models import Usuario, Rol
from Herramienta.usuarios.forms import RegistrationForm, LoginForm, RequestResetForm, ResetPasswordForm, EditarUsuarioForm
import sys

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
    usuarios = Usuario.query.order_by(Usuario.id.desc()).paginate(page=page, per_page=5)
    return render_template("usuarios/usuarios.html", title="Usuarios", usuarios=usuarios)


@usuarios.route("/cuenta", methods=["GET", "POST"])
@login_required
def cuenta():
    user_id = current_user.get_id()
    user = Usuario.query.filter_by(id=user_id).first()
    rol = Rol.query.filter_by(id=user.rol_id).first()
    return render_template("usuarios/cuenta.html", title="Mi cuenta", usuario=user, rol=rol)

@usuarios.route("/usuarios/<int:usuario_id>/editar", methods=["GET", "POST"])
@login_required
def editar_usuario(usuario_id):
    user_id = current_user.get_id()
    user = Usuario.query.filter_by(id=user_id).first()
    if user.rol_id == 1:
        abort(403)
    usuario = Usuario.query.get_or_404(usuario_id)
    roles = [(r.id, r.nombre) for r in Rol.query.all()]
    form = EditarUsuarioForm(request.form)
    form.rol.choices = roles
    if form.validate_on_submit():
        usuario.login = form.login.data
        usuario.rol_id = form.rol.data
        db.session.commit()
        flash(f"Usuario actualizado exitosamente", "success")
        return redirect(url_for("usuarios.get_usuarios"))
    elif request.method == "GET":
        form.login.data = usuario.login
    return render_template("usuarios/editar_usuario.html", title="Editar usuario", form=form)
