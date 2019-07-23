from flask import render_template, url_for, flash, redirect, request, Blueprint, abort
from flask_login import login_user, current_user, logout_user, login_required
from Herramienta import db, bcrypt
from Herramienta.models import Usuario
from Herramienta.usuarios.forms import RegistrationForm, LoginForm, RequestResetForm, ResetPasswordForm
import sys

usuarios = Blueprint("usuarios", __name__)


@usuarios.route("/register", methods=["GET", "POST"])
@login_required
def register():
    user_id = current_user.get_id()
    user = Usuario.query.filter_by(id=user_id).first()
    if user.rol_id != 4:
        abort(403)
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode("utf-8")
        rol_id_int = int(form.rol.data)
        user = Usuario(login=form.login.data,
                       password=hashed_password, rol_id=rol_id_int)
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
            login_user(user, remember=form.remember.data)
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
