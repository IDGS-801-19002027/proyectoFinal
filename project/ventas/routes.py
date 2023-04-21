from flask import render_template, redirect,session,g
from flask import request
from flask import url_for
from flask import Blueprint
from flask_security import current_user
from project.models import *
from datetime import datetime
from project.main import *
from .. import db, main

from flask.helpers import get_flashed_messages, flash

from sqlalchemy import create_engine, text, desc


ventas = Blueprint('ventas', __name__)

ultimo_id = None

@ventas.route('/venta', methods=['GET', 'POST'])   
def getAllVentas():
    ventas = db.session.query(DetalleVenta.id_venta, Ventas.fecha, Arreglo.nombre, 
                            DetalleVenta.cantidad, Ventas.total,
                            Ventas.estatus ).select_from(Ventas).join(DetalleVenta).join(Arreglo).filter(Ventas.estatus == 1).all()
    session['cart'] = []

    return render_template('/admin/ventas/ventas.html', user=current_user, ventas=ventas) 


@ventas.route('/cancelarVenta', methods = ['GET', 'POST'])
def cancelaVenta():    
        id = request.args.get('id')
        print(id)
        venta =Ventas.query.filter_by(id=id).first()
        venta.estatus = 0
        db.session.commit()
        main.registrarLogs("El usuario "+current_user.nombre+" ha finalizado la venta con ID: "+str(id), 'info', 'transaccion')
        new_accion = Bitacora(accion = "Venta cancelada", descripcion = "El usuario "+current_user.email+" ha cancelado una venta con ID: "+str(id))
        db.session.add(new_accion)
        db.session.commit()
    
        flash("Venta cancelada correctamente") 

        return redirect(url_for('ventas.getAllVentas'))

@ventas.route('/finalizarVenta', methods = ['GET', 'POST'])
def finalizarVenta():    
        id = request.args.get('id')
        #print(id)
        venta =Ventas.query.filter_by(id=id).first()
        venta.estatus = 2
        db.session.commit() 
        main.registrarLogs("El usuario "+current_user.nombre+" ha cancelado la venta con ID: "+str(id), 'info', 'transaccion')
        new_accion = Bitacora(accion = "Venta finalizada", descripcion = "El usuario "+current_user.email+" ha finalizado una venta: "+str(id))
        db.session.add(new_accion)
        db.session.commit()
    
        flash("Venta finalizada")
        return redirect(url_for('ventas.getAllVentas'))


@ventas.route('/listarArreglos', methods = ['GET', 'POST'])
def listarArreglos():
    if request.method == 'POST':
        cmbArreglos = request.form.get('cmbArreglos')
        cantidad = request.form.get('cantidad') 
        return render_template('/admin/ventas/formVentas.html', user=current_user, cmbArreglos = cmbArreglos, cantidad = cantidad)

#Aqui va insertar venta
@ventas.route('/buscarVenta', methods = ['GET', 'POST'])
def buscarVenta():
      if request.method == 'POST':
        filtro = request.form['filtro']
        ventas = db.session.query(Ventas.id, Ventas.fecha, Arreglo.nombre, 
                            DetalleVenta.cantidad, Ventas.total,
                            Ventas.estatus ).select_from(Ventas).join(DetalleVenta).join(Arreglo).filter(Ventas.fecha==filtro).all() 


        return render_template('/admin/ventas/filtro.html', user=current_user, ventas=ventas)  
      

@ventas.route('/generarTicket')
def generarTicket():
      
      id = request.args.get('idDetalle')

      ventas = db.session.query(Ventas.id, Ventas.fecha, Arreglo.nombre, 
                            DetalleVenta.cantidad,Arreglo.precioVenta, Ventas.total,
                            Arreglo.descripcion).select_from(Ventas).join(DetalleVenta).join(Arreglo).filter(Ventas.id==id).all()
      print(ventas)
      nombre = ventas[0].nombre
      fecha = ventas[0].fecha
      subtotal = ventas[0].precioVenta
      total = ventas[0].total
      descripcion = ventas[0].descripcion
      

      return render_template('/admin/ventas/ticket.html', user=current_user, nombre=nombre, fecha = fecha, subtotal = subtotal, total = total, descripcion = descripcion)




@ventas.route('/insertarVenta', methods=['GET', 'POST'])
def index():
    
    if request.method =='GET':
        arreglos = Arreglo.query.all()
        return render_template('/admin/ventas/formVentas.html', arreglos =arreglos)


    if request.method == 'POST':
        arreglos = Arreglo.query.all()
        cmbArreglos = request.form.get('cmbArreglos')
        if cmbArreglos == "0":
             flash("¡Debes seleccionar un arreglo!")
             return redirect(url_for("ventas.getAllVentas"))
        
        cantidad = int(request.form.get('cantidad'))
        arregloByID = Arreglo.query.filter_by(id=cmbArreglos).first()
        nombre = arregloByID.nombre
        item = {'cmbArreglos': nombre, 'cantidad': cantidad}
        cart = session.get('cart', [])
        cart.append(item)
        session['cart'] = cart


        hoy = datetime.now()
        fechaCompleta = str(hoy)
        fechaRecortada= fechaCompleta[:10]
        fecha = fechaRecortada

        ventas = db.session.query(Arreglo).filter(Arreglo.id == cmbArreglos).all()
        precio = ventas[0].precioVenta

        subtotal = precio * int (cantidad)

        iva = subtotal * (16/100)
        
        total = subtotal + iva
        
        estatus = 1

        venta = Ventas(fecha = fecha, total = total, estatus = estatus)
        db.session.add(venta)
        db.session.commit()

        new_accion = Bitacora(accion = "Nuevo venta en proceso", descripcion = "El usuario "+current_user.email+" ha comenzado a realizar la venta con ID: "+str(id))
        db.session.add(new_accion)
        db.session.commit()
    
        main.registrarLogs("El usuario "+current_user.nombre+" ha realizado una venta con ID: "+str(id), 'info', 'transaccion')

        detalleVenta = DetalleVenta(cantidad = cantidad, subtotal = subtotal, id_arreglo = cmbArreglos, id_venta = venta.id)
        db.session.add(detalleVenta)
        db.session.commit()

        detalleArreglo = DetalleArreglo.query.filter_by(id_arreglo = cmbArreglos).all()

        cantidadArreglo = []

        idMateriaPrima = []

        cantidadMultiplicada = []


        for detalle in detalleArreglo:
              idMateriaPrima.append(detalle.id_materia_prima)
              cantidadArreglo.append(int(detalle.cantidad))

        for multiCantidad in cantidadArreglo:
                multiCantidad = multiCantidad * int(cantidad)
                cantidadMultiplicada.append(multiCantidad)
        #print(cantidadMultiplicada)

        for i in range(0, len(idMateriaPrima)):
              materiaPrima = MateriaPrima.query.filter_by(id = idMateriaPrima[i]).all()
              materiaPrima[0].cantidad = materiaPrima[0].cantidad - cantidadMultiplicada[i]
              if materiaPrima[0].cantidad < 100:
                   flash('¡Advertencia! La cantidad de {} está por agotarse quedan: {}'.format(materiaPrima[0].nombre, materiaPrima[0].cantidad))
              
              if materiaPrima[0].cantidad < 0:
                   flash('Materia prima agotada :(')
                

              db.session.query(MateriaPrima).filter(MateriaPrima.id == idMateriaPrima[i]).update({MateriaPrima.cantidad: materiaPrima[0].cantidad})
              db.session.commit()
        
    else:
      cart = session.get('cart', [])
    return render_template('/admin/ventas/formVentas.html', cart=cart, arreglos = arreglos)
     
     




       
     

     
     

      


    



      



    
          

    
    











