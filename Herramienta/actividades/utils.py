from flask import url_for, current_app, Flask
from flask_mail import Message
from Herramienta import mail
from fpdf import FPDF

app = Flask(__name__)  

def send_reports(actividad):
    user_mail = "ad.laiton10@uniandes.edu.co"
    msg = Message(subject='Retroalimentación Tarea',
                  sender='ad.laiton10@uniandes.edu.co',
                  recipients=[user_mail])
    msg.body = f'''Cordial saludo, 
Adjunto a este mensaje usted encontrará la retroalimentación correspondiente a la tarea "201920 - Tarea".

Equipo de Asistentes y Profesores
Opti.
'''
    create_pdf(actividad)
    with app.open_resource("./files/simple_demo.pdf") as fp:
        msg.attach(
        "simple_demo.pdf",
        'application/pdf',
        fp.read()
    )
    mail.send(msg)

def create_pdf(actividad):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Times", "B",size=12)
    pdf.image("Herramienta/static/images/Uniandes_logo.png", x=10, y=8, w=30)
    pdf.cell(42)
    pdf.cell(40, 5, txt="Criterios de calificación", ln=1)
    pdf.cell(42)
    pdf.cell(40, 5, txt="UNIVERSIDAD DE LOS ANDES", ln=1)
    pdf.cell(42)
    pdf.cell(40, 5, txt="DEPARTAMENTO DE INGENIERIA INDUSTRIAL", ln=1)
    pdf.cell(42)
    pdf.set_font("Times",size=12)
    pdf.cell(40, 5, txt=actividad.nombre, ln=1)
    pdf.output("Herramienta/actividades/files/simple_demo.pdf")