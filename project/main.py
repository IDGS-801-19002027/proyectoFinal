import base64
from flask import Blueprint, flash, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from flask_security import roles_accepted
#from .models import Product
from sqlalchemy import engine, MetaData
from sqlalchemy.schema import Table
from sqlalchemy.orm import sessionmaker
from flask_security.decorators import roles_required

from project.models import Arreglo, Comentarios, Compra, DetalleCompra, DetallePedido, DetalleVenta, MateriaPrima, Pedidos, Ventas
from . import db

import logging

import io
from flask import Flask, make_response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import dates as mdates
from datetime import datetime
import matplotlib.pyplot as plt
from sqlalchemy import func
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

@main.route('/grafica')
def graficaVFiltro(idArreglo):
    fechas = []
    valores = []
    
    if idArreglo != 0:
        detalleV = DetalleVenta.query.filter(DetalleVenta.id_arreglo == idArreglo).all()
    else:
        detalleV = DetalleVenta.query.all()
    print(detalleV)
    ventas = []
    for detalle in detalleV:
        venta = Ventas.query.filter_by(id=detalle.id_venta).first()
        if venta not in ventas:
            ventas.append(venta)

    for venta in ventas:
        fechas.append(venta.fecha)
    for det in detalleV:
        valores.append(det.subtotal)

    # Convierte la lista de fechas a objetos datetime
    fechas = [datetime.strptime(fecha, '%Y-%m-%d').date() for fecha in fechas]
    
    # Crea la figura de la gráfica
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)

    # Agrega los datos a la gráfica
    axis.plot(fechas, valores, color='darkorange')

    axis.scatter(fechas, valores, color='yellow')

    # Configura el eje x de la gráfica con formato de fecha
    axis.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    
    #Establece el color de fondo de la grafica
    axis.set_facecolor('#F5F5F5')
    #Establece una etiqueta en los vectores de x, y
    axis.set_xlabel('Día de venta')
    axis.set_ylabel('Ventas (en pesos)')
    #Establece un titulo a la grafica
    axis.set_title('Promedio de ventas')

    # Agrega los valores en los puntos
    for fecha, valor in zip(fechas, valores):
        axis.text(fecha, valor, str(valor))

    # Genera la imagen de la gráfica
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)

    # Crea la respuesta HTTP con la imagen de la gráfica
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'

    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)

    # Convierte la imagen a base64
    encoded_img = base64.b64encode(output.getvalue()).decode('utf-8')

    # Crea la respuesta HTTP con la imagen de la gráfica en base64
    response = make_response(encoded_img)
    response.mimetype = 'text/plain'
    encoded_img = base64.b64encode(output.getvalue()).decode('utf-8')

    return encoded_img

@main.route('/grafica')
def graficaV():
    fechas = []
    valores = []
    
    detalleV = DetalleVenta.query.all()
    ventas = Ventas.query.all()

    for venta in ventas:
        fechas.append(venta.fecha)
    for det in detalleV:
        valores.append(det.subtotal)

    # Convierte la lista de fechas a objetos datetime
    fechas = [datetime.strptime(fecha, '%Y-%m-%d').date() for fecha in fechas]
    
    # Crea la figura de la gráfica
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)

    # Agrega los datos a la gráfica
    axis.plot(fechas, valores, color='darkorange')

    axis.scatter(fechas, valores, color='yellow')

    # Configura el eje x de la gráfica con formato de fecha
    axis.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    
    #Establece el color de fondo de la grafica
    axis.set_facecolor('#F5F5F5')
    #Establece una etiqueta en los vectores de x, y
    axis.set_xlabel('Día de venta')
    axis.set_ylabel('Ventas (en pesos)')
    #Establece un titulo a la grafica
    axis.set_title('Promedio de ventas')

    # Agrega los valores en los puntos
    for fecha, valor in zip(fechas, valores):
        axis.text(fecha, valor, str(valor))

    # Genera la imagen de la gráfica
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)

    # Crea la respuesta HTTP con la imagen de la gráfica
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'

    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)

    # Convierte la imagen a base64
    encoded_img = base64.b64encode(output.getvalue()).decode('utf-8')

    # Crea la respuesta HTTP con la imagen de la gráfica en base64
    response = make_response(encoded_img)
    response.mimetype = 'text/plain'
    encoded_img = base64.b64encode(output.getvalue()).decode('utf-8')

    return encoded_img

@main.route('/graficaInsumos')
def graficaInsumos(idInsumo):
    valores = []
    materia = []
    if idInsumo == '0':
        Insumos = MateriaPrima.query.all()
    else:
        Insumos = MateriaPrima.query.filter_by(id=idInsumo)

    for insumo in Insumos:
        materia.append(insumo.nombre)
        valores.append(insumo.cantidad)
    plt.figure(figsize=(17, 15)) 
    plt.bar(materia, valores, color='darkorange')
    plt.title("Estatus de inventario")
    plt.xlabel("Materia Prima")
    plt.ylabel("Existencias")

    for i, v in enumerate(valores):
        plt.text(i, v, str(v), ha='center')

    plt.xticks(rotation=90)
     # Convertir la imagen en formato PNG y guardarla en un buffer de memoria
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Codificar la imagen en base64 y retornarla
    imagen_codificada = base64.b64encode(buffer.read()).decode()
    return imagen_codificada

@main.route('/graficaPedidos')
def graficaPedidos(idArreglo):
    fechas = []
    valores = []
    cantidades = []

    if idArreglo =='0':
        detalleC = db.session.query(DetallePedido.id_pedido, func.sum(DetallePedido.subtotal)).group_by(DetallePedido.id_pedido).all()
    else:
        detalleC = db.session.query(DetallePedido.id_pedido, func.sum(DetallePedido.subtotal)).filter(DetallePedido.id_arreglo == idArreglo).group_by(DetallePedido.id_pedido).all()
    
    pedidos = []
    for detalle in detalleC:
        pedido = Pedidos.query.filter_by(id=detalle.id_pedido).first()
        if pedido not in pedidos:
            pedidos.append(pedido)

    for pedido in pedidos:
        fechas.append(pedido.fechaPedido)
    for det in detalleC:    
        valores.append(det[1])
        

    # Convierte la lista de fechas a objetos datetime
    fechas = [datetime.strptime(fecha, '%Y-%m-%d').date() for fecha in fechas]
    
    # Crea la figura de la gráfica
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)

    # Agrega los datos a la gráfica
    axis.plot(fechas, valores, color='darkorange')

    axis.scatter(fechas, valores, color='yellow')

    # Configura el eje x de la gráfica con formato de fecha
    axis.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    
    #Establece el color de fondo de la grafica
    axis.set_facecolor('#F5F5F5')
    #Establece una etiqueta en los vectores de x, y
    axis.set_xlabel('Fechas de pedidos')
    axis.set_ylabel('Valores (en pesos)')
    #Establece un titulo a la grafica
    axis.set_title('Historial de pedidos')

    # Agrega los valores en los puntos
    for fecha, cantidad in zip(fechas, cantidades):
        axis.text(fecha, cantidad, str(cantidad))

    # Genera la imagen de la gráfica
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)

    # Crea la respuesta HTTP con la imagen de la gráfica
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'

    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)

    # Convierte la imagen a base64
    encoded_img = base64.b64encode(output.getvalue()).decode('utf-8')

    # Crea la respuesta HTTP con la imagen de la gráfica en base64
    response = make_response(encoded_img)
    response.mimetype = 'text/plain'
    encoded_img = base64.b64encode(output.getvalue()).decode('utf-8')

    return encoded_img

@main.route('/graficaCompras')
def graficaCompras(idInsumo):
    fechas = []
    valores = []
    cantidades = []

    if idInsumo == '0':
        detalleC = db.session.query(DetalleCompra.idCompra, func.sum(DetalleCompra.cantidad), func.sum(DetalleCompra.costo)).group_by(DetalleCompra.idCompra).all()
    else:
        detalleC = db.session.query(DetalleCompra.idCompra, func.sum(DetalleCompra.cantidad), func.sum(DetalleCompra.costo)).filter(DetalleCompra.idMateria == idInsumo).group_by(DetalleCompra.idCompra).all()
    
    compras = Compra.query.filter(Compra.idCompra.in_(detalleC)).all()
    compras = []
    for detalle in detalleC:
        compra = Compra.query.filter_by(idCompra=detalle.idCompra).first()
        if compra not in compras:
            compras.append(compra)
    
    for compra in compras:
        fechas.append(compra.fecha)
    for det in detalleC:
        valores.append(det[2])
        cantidades.append(det[1])

    # Convierte la lista de fechas a objetos datetime
    #fechas = [datetime.strptime(fecha, '%Y-%m-%d').date() for fecha in fechas]
    
    # Crea la figura de la gráfica
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)

    # Agrega los datos a la gráfica
    axis.plot(fechas, valores, color='darkorange')

    axis.scatter(fechas, valores, color='yellow')

    # Configura el eje x de la gráfica con formato de fecha
    axis.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    
    #Establece el color de fondo de la grafica
    axis.set_facecolor('#F5F5F5')
    #Establece una etiqueta en los vectores de x, y
    axis.set_xlabel('Día de compra')
    axis.set_ylabel('Compras (en pesos)')
    #Establece un titulo a la grafica
    axis.set_title('Historial de compras')

    # Agrega los valores en los puntos
    for fecha, cantidad in zip(fechas, cantidades):
        axis.text(fecha, cantidad, str(cantidad))

    # Genera la imagen de la gráfica
    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)

    # Crea la respuesta HTTP con la imagen de la gráfica
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'

    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)

    # Convierte la imagen a base64
    encoded_img = base64.b64encode(output.getvalue()).decode('utf-8')

    # Crea la respuesta HTTP con la imagen de la gráfica en base64
    response = make_response(encoded_img)
    response.mimetype = 'text/plain'
    encoded_img = base64.b64encode(output.getvalue()).decode('utf-8')
    
    return encoded_img

@main.route('/moduloGrafica', methods=['GET', 'POST'])
@login_required
@roles_accepted('Administrador')
def moduloGrafica():
    valores = []
    imagen = graficaV()
    detalleV = DetalleVenta.query.all()

    for det in detalleV:
        valores.append(det.subtotal)
    suma = 0.0
    for valor in valores:
        suma = suma + float(valor)

    promedio = suma/len(valores)
    promedio = round(promedio, 2)
    
    if request.method == 'POST':
        graficaR = request.form.get('grafica')
        arregloR = request.form.get('arreglo')
        insumoR = request.form.get('insumo')
        print(insumoR)
        
        if graficaR == '1':
            if arregloR !='0' :
                imagen = graficaVFiltro(arregloR)
            else:
                imagen = graficaV()
        elif graficaR == '2':
            imagen = graficaInsumos(insumoR)
        elif graficaR == '3':
            imagen = graficaCompras(insumoR)
        elif graficaR == '4':
            imagen = graficaPedidos(arregloR)

    return render_template('grafica.html', arreglos=Arreglo.query.all(), 
                           detalleV=DetalleVenta.query.all(),
                           insumos = MateriaPrima.query.all(),
                           imagen=imagen)

@main.route('/imprimirEstadistica')
def printEstadistica():
    return render_template('admin/estadisticas.html')

 
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