import os
from flask import render_template, url_for, flash, redirect, request, Blueprint, abort, current_app
from flask_login import current_user, login_required
from Herramienta.models import Usuario, Curso, Semestre, Actividad, Punto, Inciso, Criterio, Subcriterio, Variacion
from Herramienta import db, bcrypt
from Herramienta.actividades.forms import CrearActividadArchivoForm, EliminarActividad
from openpyxl import load_workbook, Workbook

actividades = Blueprint("actividades", __name__)

@actividades.route("/actividades/<int:curso_id>/<int:actividad_id>", methods=["GET", "POST"])
@login_required
def ver_actividad(actividad_id,curso_id):
    actividad = Actividad.query.get_or_404(actividad_id)
    return render_template("actividades/ver_actividad.html", title="Ver actividad", actividad=actividad, curso_id=curso_id)

@actividades.route("/actividades/<int:curso_id>/<int:actividad_id>/eliminar", methods=["GET", "POST"])
@login_required
def eliminar_actividad(actividad_id, curso_id):
    user_id = current_user.get_id()
    user = Usuario.query.filter_by(id=user_id).first()
    if user.rol_id == 1:
        abort(403)
    actividad = Actividad.query.get_or_404(actividad_id)
    curso_idEliminar = actividad.curso_id
    semestre_idEliminar = actividad.semestre_id
    curso = Curso.query.get_or_404(curso_idEliminar)
    semestre = Semestre.query.get_or_404(semestre_idEliminar)
    form = EliminarActividad()
    if form.validate_on_submit():
        curso.actividades.remove(actividad)
        semestre.actividades.remove(actividad)
        db.session.delete(actividad)
        db.session.commit()
        flash(f"Semestre eliminado exitosamente", "success")
        return redirect(url_for("cursos.ver_curso", curso_id=curso.id))
    return render_template("actividades/eliminar_actividad.html", title="Eliminar actividad", curso_id=curso_id, form=form)

@actividades.route("/actividades/<int:actividad_id>/modificar", methods=["GET", "POST"])
@login_required
def modificar_actividad(actividad_id):
    actividad = Actividad.query.get_or_404(actividad_id)
    return render_template("actividades/ver_actividad.html", title="Ver actividad", actividad=actividad)

@actividades.route("/actividades/<int:curso_id>/crearActividad")
@login_required
def crear_actividad(curso_id):
    return render_template("actividades/crear_actividad.html", title="Crear actividad", curso_id=curso_id)

@actividades.route("/actividades/<int:curso_id>/crearActividadArchivo", methods=["GET", "POST"])
@login_required
def crear_actividadArchivo(curso_id):
    form = CrearActividadArchivoForm()
    if form.validate_on_submit():
        if form.archivo.data:
            if request.method == 'POST':
                f = request.files['archivo']
                f.save(os.path.join(current_app.root_path, 'static/files', "Actividad.xlsx"))
                analisis = analizarArchivo(curso_id)
                if analisis:
                    flash(f"Actividad creada exitosamente", "success")
                    return redirect(url_for("cursos.ver_curso", curso_id=curso_id))
                else:
                    flash(f"El archivo no pudo ser procesado porque no cumple con la estructura.", "danger")
                    return redirect(url_for("cursos.ver_curso", curso_id=curso_id))
    return render_template("actividades/crear_actividadArchivo.html", title="Crear actividad desde archivo", curso_id=curso_id, form=form)


def analizarArchivo(curso_id):
    exito = True
    archivoExcel = load_workbook(current_app.root_path + '/static/files/Actividad.xlsx')
    hoja = archivoExcel.active
    nombre = hoja["B1"].value
    nombreSemestre = hoja["B2"].value
    porcentaje = float(hoja["B6"].value)
    #Falta mandar errores cuando el semestre no existe. De igual cuando no cumple con cosas como que es un número y eso. 
    semestre = Semestre.query.filter_by(nombre=nombreSemestre).first()
    actividad = Actividad(nombre=nombre, porcentaje=porcentaje, habilitada=False, semestre_id=semestre.id, curso_id=curso_id)
    db.session.add(actividad)
    db.session.commit()
    #Siempre se debe comenzar ahí, el formato se tiene que respetar.
    fila = 10
    columna = 2
    final = False
    celdaPunto = hoja.cell(row=fila, column=columna).value

    while not final:
        if celdaPunto is not None:
            punto = Punto(nombre=celdaPunto, actividad_id=actividad.id, puntajePosible=0)
            db.session.add(punto)
            db.session.commit()
            finalPunto = False
            fila = fila + 1
            columna = columna + 1
            celdaInciso = hoja.cell(row=fila, column=columna).value
            #-------------------------------------------------------------------
            while not finalPunto:
                inciso = Inciso(nombre = celdaInciso, puntajePosible=0, punto_id=punto.id)
                db.session.add(inciso)
                db.session.commit()
                finalInciso = False
                fila = fila + 1
                columna = columna + 1
                celdaCriterio = hoja.cell(row=fila, column=columna).value
                #-------------------------------------------------------------------
                while not finalInciso:
                    criterio = Criterio(nombre = celdaCriterio, puntajePosible=0, inciso_id=inciso.id)
                    db.session.add(criterio)
                    db.session.commit()
                    finalCriterio = False
                    fila = fila + 1
                    columna = columna + 1
                    celdaSubriterio = hoja.cell(row=fila, column=columna).value
                    #-------------------------------------------------------------------
                    while not finalCriterio:
                        puntajeMinimo = int(hoja.cell(row=fila, column=7).value)
                        puntajeMaximo = int(hoja.cell(row=fila, column=8).value)
                        subcriterio = Subcriterio(nombre = celdaSubriterio, maximoPuntaje=puntajeMaximo, minimoPuntaje=puntajeMinimo, criterio_id=criterio.id)
                        db.session.add(subcriterio)
                        db.session.commit()
                        finalSubcriterio = False
                        fila = fila + 1
                        columna = columna + 1
                        celdaVariacion = hoja.cell(row=fila, column=columna).value
                        #-------------------------------------------------------------------
                        while not finalSubcriterio:
                            maximoVeces = int(hoja.cell(row=fila, column=9).value)
                            puntaje = int(hoja.cell(row=fila, column=8).value)
                            esPenalizacion = False
                            if puntaje < 0:
                                esPenalizacion = True
                            variacion = Variacion(descripcion = celdaVariacion, puntaje=puntaje, esPenalizacion=esPenalizacion, subcriterio_id=subcriterio.id, esOtro=False, maximoVeces=maximoVeces)
                            db.session.add(variacion)
                            db.session.commit()
                            subcriterio.variaciones.append(variacion)
                            db.session.commit()
                            fila = fila + 1
                            celdaVariacion = hoja.cell(row=fila, column=columna).value
                            if celdaVariacion is None:
                                finalSubcriterio = True
                        #-------------------------------------------------------------------
                        columna = columna - 1
                        celdaSubriterio = hoja.cell(row=fila, column=columna).value
                        if celdaSubriterio is None:
                            finalCriterio = True
                        criterio.puntajePosible = criterio.puntajePosible + subcriterio.maximoPuntaje
                        criterio.subcriterios.append(subcriterio)
                        db.session.commit()
                    #-------------------------------------------------------------------
                    columna = columna - 1
                    celdaCriterio = hoja.cell(row=fila, column=columna).value
                    if celdaCriterio is None:
                        finalInciso = True
                    inciso.puntajePosible = inciso.puntajePosible + criterio.puntajePosible
                    inciso.criterios.append(criterio)
                    db.session.commit()
                #-------------------------------------------------------------------
                columna = columna - 1
                celdaInciso = hoja.cell(row=fila, column=columna).value
                if celdaInciso is None:
                    finalPunto = True
                punto.puntajePosible = punto.puntajePosible + inciso.puntajePosible
                punto.incisos.append(inciso)
                db.session.commit()
            #-------------------------------------------------------------------
            columna = columna - 1
            celdaPunto = hoja.cell(row=fila, column=columna).value
            actividad.puntos.append(punto)
            db.session.commit()
        else:
            final = True
    return exito            
@actividades.route("/actividades/<int:curso_id>/crearActividadWeb", methods=["GET", "POST"])
@login_required
def crear_actividadWeb(curso_id):
    return render_template("actividades/crear_actividadWeb.html", title="Crear actividad Web", curso_id=curso_id)

@actividades.route("/actividades/<int:actividad_id>/descargar", methods=["GET"])
@login_required
def descargar_actividad(actividad_id):
    actividad = Actividad.query.get_or_404(actividad_id)
    semestre = Semestre.query.get_or_404(actividad.semestre_id)
    curso = Curso.query.get_or_404(actividad.curso_id)
    wb = Workbook()
    dest_filename = 'ExportarActividad.xlsx'
    ws = wb.active
    ws.cell(column=1, row=1, value="Nombre:")
    ws.cell(column=2, row=1, value=actividad_id.nombre)
    ws.cell(column=1, row=2, value="Semestre:")
    ws.cell(column=2, row=2, value=semestre.nombre)
    ws.cell(column=1, row=3, value="ID Tarea:")
    ws.cell(column=1, row=4, value="Creado:")
    ws.cell(column=1, row=5, value="Curso:")
    ws.cell(column=1, row=5, value=curso.nombre)
    ws.cell(column=1, row=6, value="Porcentaje sobre la nota:")
    ws.cell(column=1, row=6, value=actividad.porcentaje)
    ws.cell(column=1, row=7, value="Nota estándar:")
    ws.cell(column=1, row=8, value="Integrantes por grupo:")


    wb.save(filename = dest_filename)
    return render_template("actividades/descargar_actividad.html", title="Descargar actividad Web", actividad_id=actividad_id)
