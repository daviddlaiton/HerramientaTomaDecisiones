import os
from flask import render_template, url_for, flash, redirect, request, Blueprint, abort, current_app, send_file
from flask_wtf import FlaskForm
from wtforms import FieldList, FormField, SubmitField
from flask_login import current_user, login_required
from Herramienta.models import Usuario, Curso, Semestre, Actividad, Punto, Inciso, Criterio, Subcriterio, Variacion, Grupo, Estudiante
from Herramienta import db, bcrypt
from Herramienta.actividades.forms import CrearActividadArchivoForm, EliminarActividad, DescargarActividad, CrearPunto, CambiarEstadoActividad, EnviarReportes, IntegranteForm
from openpyxl import load_workbook, Workbook
from Herramienta.actividades.utils import send_reports

actividades = Blueprint("actividades", __name__)

@actividades.route("/actividades/<int:curso_id>/<int:actividad_id>", methods=["GET", "POST"])
@login_required
def ver_actividad(actividad_id,curso_id):
    actividad = Actividad.query.get_or_404(actividad_id)
    return render_template("actividades/ver_actividad.html", title="Ver actividad", actividad=actividad, curso_id=curso_id)

@actividades.route("/actividades/<int:curso_id>/<int:actividad_id>/calificar", methods=["GET", "POST"])
@login_required
def calificar_actividad(actividad_id,curso_id):
    actividad = Actividad.query.get_or_404(actividad_id)
    puntos = []
    for punto in actividad.puntos:
        incisos = []
        for inciso in punto.incisos:
            criterios = []
            for criterio in inciso.criterios:
                subcriterios = []
                for subcriterio in criterio.subcriterios:
                    variaciones = []
                    for variacion in subcriterio.variaciones:
                        variacionJSON = {
                            "id" : variacion.id,
                            "puntaje" : variacion.puntaje
                        }
                        variaciones.append(variacionJSON)
                    subcriterioJSON = {
                        "id" : subcriterio.id,
                        "variaciones" : variaciones
                    }
                    subcriterios.append(subcriterioJSON)
                criterioJSON = {
                    "id" : criterio.id,
                    "subcriterios" : subcriterios
                }
                criterios.append(criterioJSON)
            incisoJSON = {
                "id" : inciso.id,
                "criterios" : criterios
            }
            incisos.append(incisoJSON)
        puntoJSON = {
            "id" : punto.id,
            "incisos" : incisos
        }
        puntos.append(puntoJSON)
    actividadToJson = {
        "id" : actividad.id,
        "puntos" : puntos
    }
    return render_template("actividades/calificar_actividad.html", title="Calificar actividad", actividad=actividad, curso_id=curso_id, actividadJSON = actividadToJson)

@actividades.route("/actividades/<int:curso_id>/<int:actividad_id>/eliminar", methods=["GET", "POST"])
@login_required
def eliminar_actividad(actividad_id, curso_id):
    user_id = current_user.get_id()
    user = Usuario.query.filter_by(id=user_id).first()
    if user.rol_id == 1:
        abort(403)
    form = EliminarActividad()
    if form.validate_on_submit():
        eliminarActividad(actividad_id)
        flash(f"Actividad eliminada exitosamente", "success")
        return redirect(url_for("cursos.ver_curso", curso_id=curso_id))
    return render_template("actividades/eliminar_actividad.html", title="Eliminar actividad", curso_id=curso_id, actividad_id=actividad_id, form=form)

@actividades.route("/actividades/<int:curso_id>/<int:actividad_id>/cambiarEstado", methods=["GET", "POST"])
@login_required
def cambiarEstado_actividad(actividad_id,curso_id):
    actividad = Actividad.query.get_or_404(actividad_id)
    estadoACambiar = not actividad.habilitada
    print(estadoACambiar)
    form = CambiarEstadoActividad()
    if form.validate_on_submit():
        actividad.habilitada = estadoACambiar
        db.session.commit()
        flash(f"Cambio de estado de actividad realizado exitosamente", "success")
        return redirect(url_for("actividades.ver_actividad", curso_id=curso_id, actividad_id=actividad_id))
    return render_template("actividades/cambiarEstado_actividad.html", title="Cambiar estado actividad", actividad=actividad, curso_id=curso_id, form=form)

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
    numeroIntegrantes = int(hoja["B8"].value)
    #Falta mandar errores cuando el semestre no existe. De igual cuando no cumple con cosas como que es un número y eso. 
    semestre = Semestre.query.filter_by(nombre=nombreSemestre).first()
    actividad = Actividad(nombre=nombre, porcentaje=porcentaje, habilitada=False, semestre_id=semestre.id, curso_id=curso_id, numeroIntegrantes=numeroIntegrantes)
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
                        puntajeMinimo = float(hoja.cell(row=fila, column=7).value)
                        puntajeMaximo = float(hoja.cell(row=fila, column=8).value)
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
                            puntaje = float(hoja.cell(row=fila, column=8).value)
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

@actividades.route("/actividades/<int:curso_id>/<int:actividad_id>/descargar", methods=["GET","POST"])
@login_required
def descargar_actividad(actividad_id,curso_id):
    actividad = Actividad.query.get_or_404(actividad_id)
    semestre = Semestre.query.get_or_404(actividad.semestre_id)
    curso = Curso.query.get_or_404(actividad.curso_id)
    form = DescargarActividad()
    wb = Workbook()
    dest_filename = 'Herramienta/static/files/ExportarActividad.xlsx'
    hoja = wb.active
    hoja.cell(column=1, row=1, value="Nombre:")
    hoja.cell(column=2, row=1, value=actividad.nombre)
    hoja.cell(column=1, row=2, value="Semestre:")
    hoja.cell(column=2, row=2, value=semestre.nombre)
    hoja.cell(column=1, row=3, value="ID Tarea:")
    hoja.cell(column=1, row=4, value="Creado:")
    hoja.cell(column=1, row=5, value="Curso:")
    hoja.cell(column=1, row=5, value=curso.nombre)
    hoja.cell(column=1, row=6, value="Porcentaje sobre la nota:")
    hoja.cell(column=1, row=6, value=actividad.porcentaje)
    hoja.cell(column=1, row=7, value="Nota estándar:")
    hoja.cell(column=1, row=8, value="Integrantes por grupo:")


    hoja.cell(column=1, row=9, value="ID")
    hoja.cell(column=2, row=9, value="Punto")
    hoja.cell(column=3, row=9, value="Inciso")
    hoja.cell(column=4, row=9, value="Criterio")
    hoja.cell(column=5, row=9, value="Subcriterio")
    hoja.cell(column=6, row=9, value="Variación/Penalización")
    hoja.cell(column=7, row=9, value="Puntaje minimo")
    hoja.cell(column=8, row=9, value="Puntaje")
    hoja.cell(column=9, row=9, value="Máximo veces")

    
    #------------------------------------------------------------------
    fila = 10
    idPunto = 1
    idInciso = 1
    idCriterio = 1
    idSubcriterio = 1
    idVariacion = 1

    for punto in actividad.puntos:
        hoja.cell(column=1, row=fila, value=idPunto)
        hoja.cell(column=2, row=fila, value=punto.nombre)
        idPunto = idPunto + 1
        fila = fila + 1
        for inciso in punto.incisos:
            hoja.cell(column=1, row=fila, value=idInciso)
            hoja.cell(column=3, row=fila, value=inciso.nombre)
            idInciso = idInciso + 1
            fila = fila + 1
            for criterio in inciso.criterios:
                hoja.cell(column=1, row=fila, value=idCriterio)
                hoja.cell(column=4, row=fila, value=criterio.nombre)
                idCriterio = idCriterio + 1
                fila = fila + 1
                for subcriterio in criterio.subcriterios:
                    hoja.cell(column=1, row=fila, value=idSubcriterio)
                    hoja.cell(column=5, row=fila, value=subcriterio.nombre)
                    hoja.cell(column=7, row=fila, value=subcriterio.minimoPuntaje)
                    hoja.cell(column=8, row=fila, value=subcriterio.maximoPuntaje)
                    idSubcriterio = idSubcriterio + 1
                    fila = fila + 1
                    for variacion in subcriterio.variaciones:
                        hoja.cell(column=1, row=fila, value=idVariacion)
                        hoja.cell(column=6, row=fila, value=variacion.descripcion)
                        hoja.cell(column=8, row=fila, value=variacion.puntaje)
                        hoja.cell(column=9, row=fila, value=variacion.maximoVeces)
                        idVariacion = idVariacion + 1
                        fila = fila + 1
    hoja.column_dimensions['E'].width = 10
    hoja.column_dimensions['F'].width = 200
    wb.save(filename = dest_filename)
    if form.validate_on_submit():
        return send_file('static/files/ExportarActividad.xlsx',
                     mimetype='text/xlsx',
                     attachment_filename='ExportarActividad.xlsx',
                     as_attachment=True)
    return render_template("actividades/descargar_actividad.html", title="Descargar actividad Web", actividad_id=actividad_id, curso_id=curso_id, form=form)

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

@actividades.route("/actividades/<int:curso_id>/<int:actividad_id>/crearPunto", methods=["GET","POST"])
@login_required
def crear_punto(curso_id,actividad_id):
    actividad = Actividad.query.get_or_404(actividad_id)
    # form = EliminarActividad()
    # punto = Punto(nombre=, actividad_id=actividad.id, puntajePosible=0)

@actividades.route("/actividades/<int:curso_id>/<int:actividad_id>/enviarInformes", methods=["GET","POST"])
@login_required
def enviar_informes(curso_id,actividad_id):
    actividad = Actividad.query.get_or_404(actividad_id)
    form = EnviarReportes()
    if form.validate_on_submit():
        send_reports(actividad)
        flash(f"Informes enviados exitosamente", "success")
        return render_template("actividades/ver_actividad.html", title="Ver actividad", actividad=actividad, curso_id=curso_id)
    return render_template("actividades/enviarReportes.html", title="Enviar reportes", actividad_id=actividad_id, curso_id=curso_id, form=form)

@actividades.route("/actividades/<int:curso_id>/<int:actividad_id>/verGrupos", methods=["GET", "POST"])
@login_required
def ver_grupos_actividad(actividad_id,curso_id):
    actividad = Actividad.query.get_or_404(actividad_id)
    return render_template("actividades/ver_grupos_actividad.html", title="Ver grupos", actividad=actividad, curso_id=curso_id)

@actividades.route("/actividades/<int:curso_id>/<int:actividad_id>/crearGrupo/<int:numero_integrantes>", methods=["GET", "POST"])
@login_required
def crear_grupo_actividad(actividad_id,curso_id, numero_integrantes):
    actividad = Actividad.query.get_or_404(actividad_id)
    grupos = Grupo.query.filter_by(actividad_id=actividad_id).first()
    semestre = Semestre.query.filter_by(id=actividad.semestre_id).first()
    estudiantesActuales = []
    if grupos is not None:
        estudiantesActuales = [(e) for e in grupos.estudiantes]
    estudiantes = [(e.id, e.login)
              for e in Estudiante.query.all() if e not in estudiantesActuales and semestre in e.semestres]
    class CrearGrupo(FlaskForm):pass
    CrearGrupo.integrantes = FieldList(FormField(IntegranteForm), min_entries=numero_integrantes)
    CrearGrupo.submit = SubmitField("Crear grupo")
    form = CrearGrupo()
    opciones = IntegranteForm()
    opciones.codigo.choices = estudiantes
    if form.validate_on_submit():
        flash(f"Informes enviados exitosamente", "success")
        return render_template("actividades/ver_actividad.html", title="Ver actividad", actividad=actividad, curso_id=curso_id)
    return render_template("actividades/crear_grupo_actividad.html", title="Crear grupos", actividad=actividad, curso_id=curso_id, form=form, opciones=opciones, numero_integrantes=numero_integrantes)
