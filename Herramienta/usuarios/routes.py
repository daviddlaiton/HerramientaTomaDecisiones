import random
import string
from flask import render_template, url_for, flash, redirect, request, Blueprint, abort
from flask_login import login_user, current_user, logout_user, login_required
from Herramienta import db, bcrypt
from Herramienta.models import Usuario, Rol, Curso, ListaUsuariosSemestreCurso, Semestre
from Herramienta.usuarios.forms import (RegistrationForm, LoginForm, RequestResetForm, ResetPasswordForm,
                                        EditarNombreUsuarioForm, EditarRolUsuarioForm, AgregarCursoAUsuarioForm, EliminarCursosAUsuarioForm,
                                        EliminarUsuarioForm, EstablecerContraseñaForm, ActivarUsuarioForm, EliminarMonitorAsignadoForm, CrearMonitorForm)
from Herramienta.usuarios.utils import send_reset_email,usuario_creado_email

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
    password = randomString(10)
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        user = Usuario(login=form.login.data,
                       password=hashed_password, rol_id=form.rol.data, activado=False)
        db.session.add(user)
        db.session.commit()
        usuario = Usuario.query.filter_by(login=form.login.data).first()
        usuario_creado_email(usuario)
        flash(f"Usuario creado exitosamente. Es necesario que este usuario establezca su propia contraseña.", "success")
        return redirect(url_for("usuarios.get_usuarios"))
    return render_template("usuarios/crear_usuario.html", title="Crear usuario", form=form)

@usuarios.route("/crearMonitor/<int:curso_id>/<int:semestre_id>", methods=["GET", "POST"])
@login_required
def crearMonitor(curso_id,semestre_id):
    user_id = current_user.get_id()
    user = Usuario.query.filter_by(id=user_id).first()
    if user.rol_id == 1:
        abort(403)
    form = CrearMonitorForm()
    password = randomString(10)
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        user = Usuario(login=form.login.data,
                       password=hashed_password, rol_id=1, activado=False)
        db.session.add(user)
        db.session.commit()
        usuario = Usuario.query.filter_by(login=form.login.data).first()
        usuario_creado_email(usuario)
        flash(f"Monitor creado exitosamente. Es necesario que este usuario establezca su propia contraseña.", "success")
        return redirect(url_for("usuarios.verMonitores", curso_id=curso_id, semestre_id=semestre_id))
    return render_template("usuarios/crear_monitor.html", title="Crear monitor", form=form)

@usuarios.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = Usuario.query.filter_by(login=form.login.data).first()
        if user:
            send_reset_email(user)
            flash('Un correo ha sido enviado con las instrucciones para el cambio de la contraseña.', 'info')
            return redirect(url_for('usuarios.login'))
        else:
            flash("El login ingresado no existe en el Opticorrector", "danger")
    return render_template('usuarios/reset_password.html', title='Reset Password', form=form)

@usuarios.route("/resetPassword/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = Usuario.verify_token_password(token)
    if user is None:
        flash('El link de cambio de contraseña ha expirado. Necesitas crear uno nuevo de la misma manera en que creaste el anterior', 'warning')
        return redirect(url_for('main.home'))
    form = EstablecerContraseñaForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('La constreña ha sido definida. Ya puedes iniciar sesión.', 'success')
        return redirect(url_for('usuarios.login'))
    return render_template('usuarios/establecerContrasena.html', title='Cambiar contraseña', form=form)

@usuarios.route("/resetPassword/<int:usuario_id>", methods=["GET", "POST"])
def cambiar_contrasena(usuario_id):
    user = Usuario.query.get_or_404(usuario_id)
    form = EstablecerContraseñaForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('La constreña ha sido definida', 'success')
        return redirect(url_for('cursos.get_cursos'))
    return render_template('usuarios/establecerContrasena.html', title='Cambiar contraseña', form=form)


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
            return redirect(next_page) if next_page else redirect(url_for("main.home"))
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
        return redirect(url_for("usuarios.ver_usuario", usuario_id=usuario.id))
    return render_template("usuarios/anadirCurso_usuario.html", title="Anadir cursos a usuario", form=form, usuario=usuario, cursos=cursos)


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
        usuario.cursos.remove(curso)
        db.session.commit()
        flash(f"Curso eliminado exitosamente", "success")
        return redirect(url_for("usuarios.ver_usuario", usuario_id=usuario.id))
    return render_template("usuarios/eliminarCurso_usuario.html", title="Eliminar curso a usuario", form=form, usuario=usuario, curso=curso)


@usuarios.route("/usuarios/<int:usuario_id>/eliminarUsuario", methods=["GET", "POST"])
@login_required
def eliminar_usuario(usuario_id):
    user_id = current_user.get_id()
    user = Usuario.query.filter_by(id=user_id).first()
    if user.rol_id == 1:
        abort(403)
    usuario = Usuario.query.get_or_404(usuario_id)
    form = EliminarUsuarioForm()
    if form.validate_on_submit():
        lista = ListaUsuariosSemestreCurso.query.filter_by(usuario_id=usuario.id).first()
        db.session.delete(lista)
        db.session.delete(usuario)
        db.session.commit()
        flash(f"Usuario eliminado exitosamente", "success")
        return redirect(url_for("usuarios.get_usuarios"))
    return render_template("usuarios/eliminar_usuario.html", title="Eliminar usuario", form=form, usuario=usuario)

def randomString(stringLength):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(stringLength))

@usuarios.route("/usuarios/activarUsuario", methods=["GET", "POST"])
@login_required
def activar_usuario():
    user_id = current_user.get_id()
    user = Usuario.query.filter_by(id=user_id).first()
    form = ActivarUsuarioForm()
    if form.validate_on_submit():
        user.nombres = form.nombres.data
        user.apellidos = form.apellidos.data
        user.activado = True
        db.session.commit()
        flash(f"Usuario activado exitosamente", "success")
        return redirect(url_for("cursos.get_cursos"))
    return render_template("usuarios/activar_usuario.html", title="Activar usuario", form=form)

@usuarios.route("/usuarios/<int:semestre_id>/<int:curso_id>/verMonitores", methods=["GET", "POST"])
@login_required
def verMonitores(semestre_id,curso_id):
    curso = Curso.query.get_or_404(curso_id)
    semestre = Semestre.query.get_or_404(semestre_id)
    listaMonitores = ListaUsuariosSemestreCurso.query.filter_by(semestre_id=semestre_id,curso_id=curso_id).all()
    monitores = []
    for monitorEnLista in listaMonitores:
        idMonitor = monitorEnLista.usuario_id
        monitorAgregar = Usuario.query.get_or_404(idMonitor)
        monitores.append(monitorAgregar)
    return render_template("usuarios/verMonitores.html", title="Ver monitores", monitores=monitores, semestre=semestre, curso=curso)

@usuarios.route("/usuarios/<int:semestre_id>/<int:curso_id>/agregarMonitor", methods=["GET", "POST"])
@login_required
def agregarMonitor(semestre_id,curso_id):
    curso = Curso.query.get_or_404(curso_id)
    semestre = Semestre.query.get_or_404(semestre_id)
    todosLosMonitores = Usuario.query.filter_by(rol_id=1).all()
    listaMonitores = ListaUsuariosSemestreCurso.query.filter_by(semestre_id=semestre_id,curso_id=curso_id).all()
    monitoresJSON = []
    monitoresActualesJSON = []
    for monitor in todosLosMonitores:
        if monitor.activado:
            monitorAnadir = {
                "login" : monitor.login,
                "nombres" : monitor.nombres,
                "apellidos" : monitor.apellidos
            } 
            monitoresJSON.append(monitorAnadir)
    for monitor in listaMonitores:
        login = Usuario.query.get_or_404(monitor.usuario_id).login
        monitoresActualesJSON.append(login)
    return render_template("usuarios/agregarMonitor.html", title="Ver monitores", monitoresActuales=monitoresActualesJSON, monitoresJSON=monitoresJSON, semestre=semestre, curso=curso)

@usuarios.route("/usuarios/<int:semestre_id>/<int:curso_id>/agregarMonitor/<monitorSeleccionado>", methods=["GET", "POST"])
@login_required
def monitorAgregado(semestre_id,curso_id, monitorSeleccionado):
    monitor = Usuario.query.filter_by(login=monitorSeleccionado).first()
    nuevoMonitor = ListaUsuariosSemestreCurso(semestre_id=semestre_id, curso_id=curso_id, usuario_id=monitor.id)
    db.session.add(nuevoMonitor)
    db.session.commit()
    flash(f"Monitor agreagado exitosamente", "success")
    return redirect(url_for("usuarios.verMonitores", curso_id=curso_id, semestre_id=semestre_id))

@usuarios.route("/usuarios/<int:semestre_id>/<int:curso_id>/eliminarMonitorAsignado/<int:usuario_id>", methods=["GET", "POST"])
@login_required
def eliminarMonitorAsignado(semestre_id,curso_id,usuario_id):
    curso = Curso.query.get_or_404(curso_id)
    semestre = Semestre.query.get_or_404(semestre_id)
    usuario = Usuario.query.get_or_404(usuario_id)
    form = EliminarMonitorAsignadoForm()
    if form.validate_on_submit():
        eliminar = ListaUsuariosSemestreCurso.query.filter_by(semestre_id=semestre_id, curso_id=curso_id, usuario_id=usuario_id).first()
        db.session.delete(eliminar)
        db.session.commit()
        flash(f"Monitor eliminado exitosamente", "success")
        return redirect(url_for("usuarios.verMonitores", curso_id=curso_id, semestre_id=semestre_id))
    return render_template("usuarios/eliminar_monitor.html", title="Eliminar monitor", form=form, curso=curso, semestre=semestre, usuario=usuario)