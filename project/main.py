from flask import Blueprint, flash, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from flask_security import roles_accepted
#from .models import Product
from sqlalchemy import engine, MetaData
from sqlalchemy.schema import Table
from sqlalchemy.orm import sessionmaker
from flask_security.decorators import roles_required

from project.models import Comentarios
from . import db

import logging

import io
from flask import Flask, make_response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import dates as mdates
from datetime import datetime
import math

main = Blueprint('main', __name__)

@main.route("/")
def inicio():
    return render_template('index.html')

@main.route('/login', methods = ['GET', 'POST'])
def index():
    return render_template('login.html')

@main.route('/comentarios')
@login_required
@roles_accepted("Administrador")
def obtenerComentarios():
    comments = Comentarios.query.all()

    return render_template('admin/comentario/consultarComentarios.html', comentarios = comments)

@main.route('/contacto', methods = ['GET', 'POST'])
def contacto():
    if request.method == 'POST':
        email = request.form.get('correo')
        mensaje = request.form.get('mensaje')
        comentario = Comentarios(correo=email, mensaje=mensaje)

        db.session.add(comentario)
        db.session.commit()
        flash('GRACIAS POR TUS COMENTARIOS.')
        return render_template('contactanos.html')
    
    return render_template('contactanos.html')

@main.route('/sobre-nosotros', methods = ['GET', 'POST'])
def sobreNosotros():
    return render_template('sobre_nosotros.html')


def registrarLogs(mensaje, tipoMensaje, file):
    # Crea un objeto logger:
    logger = logging.getLogger(__name__)
    # Configurar el nivel de registro para el logger
    logger.setLevel(logging.INFO)
    #Crea un manejador de archivos para almacenar los logs en un archivo
    if file == 'transaccion':
        log_file = 'registroTransacciones.log'
    if file == 'error':
        log_file = 'registroErrores.log'
    if file == 'bitacora':
        log_file = 'registroBitacora.log'

    file_handler = logging.FileHandler(log_file)
    # Configura el formato del mensaje de log:
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    #Agrega el manejador de archivos al logger
    logger.addHandler(file_handler)

    if tipoMensaje == 'error':
        logger.error(mensaje)
    elif tipoMensaje == 'info':
        logger.info(mensaje)
    elif tipoMensaje == 'warn':
        logger.warn(mensaje)
    elif tipoMensaje == 'debug':
        logger.debug(mensaje)