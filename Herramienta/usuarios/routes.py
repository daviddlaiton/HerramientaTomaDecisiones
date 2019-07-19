from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from Herramienta import db, bcrypt
from Herramienta.models import Usuario
from Herramienta.usuarios.forms import RegistrationForm, LoginForm, RequestResetForm, ResetPasswordForm
import sys

usuarios = Blueprint("usuarios", __name__)

@usuarios.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        rol_id_int = int(form.rol.data)
        user = Usuario(login=form.login.data, password=hashed_password, rol_id= rol_id_int)
        db.session.add(user)
        db.session.commit()
        flash(f"Registrado exitosamente", "success")
        return redirect(url_for("usuarios.login"))
    return render_template("register.html", title="Register", form=form)

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
            return redirect(next_page) if next_page else redirect(url_for("main.home"))
        else:
            flash("Login o contraseña invalidos.", "danger")
    return render_template("login.html", title="Login", form=form)

@usuarios.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.home"))