from flask import flash, render_template, redirect
from flask import request
from flask import url_for
from flask import Blueprint
from flask_login import login_required
from flask_security import current_user
from sqlalchemy import func

from .. import db, main
from project.models import Bitacora, DetalleArreglo, DetallePedido, MateriaPrima, Pedidos, Arreglo, User

pedidos = Blueprint('pedidos', __name__) 

####### ADMIN - PEDIDOS #######
@pedidos.route("/entregas", methods=["GET"])
@login_required
def entregas():
    pedidos = db.session.query(Pedidos.id, Pedidos.fechaPedido, Pedidos.estatus ,Arreglo.nombre, DetallePedido.cantidad, func.sum(DetallePedido.subtotal)).\
    select_from(Pedidos).\
    join(DetallePedido, Pedidos.id == DetallePedido.id_pedido).\
    join(Arreglo, Arreglo.id == DetallePedido.id_arreglo).\
    group_by(Pedidos.id, Pedidos.fechaPedido, Arreglo.nombre, DetallePedido.cantidad).all()

    return render_template("admin/pedido/entregas.html", pedidos = pedidos)


@pedidos.route("/finalizarPedido/<int:id>")
@login_required
def finalizarPedido(id):
    db.session.query(Pedidos).filter(Pedidos.id == int(id)).update({"estatus": 2})
    db.session.commit()
    main.registrarLogs("El usuario "+current_user.nombre+" ha cancelado el pedido con ID: "+str(id), 'info', 'transaccion')

    flash('El Pedido.ha sido entregado.')
    return redirect(url_for("pedidos.entregas")) 




#### CLIENTE - PEDIDOS ####
@pedidos.route("/detArreglo", methods=['GET', 'POST'])
@login_required
def detArreglo():
  
    if request.method == 'GET': 
        arreglos = db.session.query(Arreglo).all()
        detArreglo = DetalleArreglo.query.all()

        flash("Compra real")

        return render_template("cliente/detArreglo.html", arreglos = arreglos, detArreglo = detArreglo )


    if request.method == 'POST': 
      
        input_fecha = request.form.get("fecha")
      
        usuario = db.session.query(User).filter(User.email == current_user.email).first()
        cantidad = request.form.getlist('cantidad[]')
        producto = request.form.getlist('id[]')

        cant = []
        prods = []
    
        ##Obtengo únicamente los productos con cantidad mayor a 0##
        for i in range(0, len(cantidad)):
            if int(cantidad[i]) > 0:
                cant.append(cantidad[i])
                prods.append(producto[i])  
      
        pedidos = db.session.query(Arreglo).filter(Arreglo.id == prods[0]).all()
        precio = pedidos[0].precioVenta 

        num = int (cant[0])

        subtotal = precio * num
      
        iva = subtotal * (16/100)
        
        total = subtotal + iva
        
        estatus = 1 

        pedido = Pedidos(fechaPedido = input_fecha, total = total, estatus = estatus )
        db.session.add(pedido)
        db.session.commit()  
        main.registrarLogs("El cliente "+current_user.nombre+" ha solicitado un pedido con ID: "+str(id), 'info', 'transaccion')
        new_accion = Bitacora(accion = "Nuevo pedido solicitado", descripcion = "El usuario "+current_user.email+" registró un nuevo pedido: "+str(id))
        db.session.add(new_accion)
        db.session.commit()
    

        for i in range(len(prods)):
            detalle_pedido = DetallePedido(cantidad = cant[0], subtotal = subtotal, id_arreglo = prods[0], id_pedido = pedido.id, id_usuario = usuario.id)
            db.session.add(detalle_pedido)
            db.session.commit()  
                
            # Obtengo completo el detalle con base al id del arreglo que se seleccionó en la vista
            detalleArreglo = db.session.query(DetalleArreglo).filter(DetalleArreglo.id_arreglo == prods[i]).all()
            
            for i in range(len(prods)):
                id_matPrima = detalleArreglo[i].id_materia_prima

                matPrima = db.session.query(MateriaPrima).filter(MateriaPrima.id == id_matPrima).all()
                cantidadArreglos = int(cant[i])
                cantMateria = detalleArreglo[i].cantidad * cantidadArreglos 
                rest = matPrima[0].cantidad - cantMateria

                db.session.query(MateriaPrima).filter(MateriaPrima.id == id_matPrima).update({MateriaPrima.cantidad: rest})
                db.session.commit()

            flash("Su pedido ha sido agregado exitosamente")


    return redirect(url_for('pedidos.arrangement'))

   
@pedidos.route('/pedido', methods = ['GET', 'POST'])
@login_required
def arrangement():

    if request.method == 'GET':
        pedidos = db.session.query(DetallePedido, Arreglo, Pedidos)\
               .join(Arreglo, Arreglo.id == DetallePedido.id)\
               .join(Pedidos, Pedidos.id == DetallePedido.id)\
               .all()
        
        query = db.session.query(DetallePedido, Arreglo, Pedidos, User)\
               .join(Arreglo, Arreglo.id == DetallePedido.id_arreglo, isouter=True)\
               .join(Pedidos, Pedidos.id == DetallePedido.id_pedido, isouter=True)\
               .join(User, User.id == DetallePedido.id_usuario, isouter=True)\
               .filter(User.email == current_user.email).all()
        
        return render_template('/cliente/pedidos.html', user=current_user, query=query)
    '''
    if request.method == 'POST':
        filtro = request.form['filtro']
        pedidos = db.session.query(Pedidos, DetallePedido, Arreglo).\
        join(DetallePedido, Pedidos.id == DetallePedido.id).\
        join(Arreglo, DetallePedido.id == Arreglo.id).filter(Pedidos.fechaPedido == filtro).all()


        return render_template('/cliente/filtro.html', user=current_user, pedidos=pedidos)
    '''

@pedidos.route('/cancelar', methods = ['GET', 'POST'])
@login_required
def cancelar():    
        id = request.args.get('id')
        pedido = Pedidos.query.filter_by(id=id).first()
        pedido.estatus = 0
        db.session.commit() 
        main.registrarLogs("El usuario "+current_user.nombre+" ha cancelado el pedido con ID: "+str(id), 'info', 'transaccion')

        new_accion = Bitacora(accion = "Pedido cancelado", descripcion = "El usuario "+current_user.email+" ha cancelado el pedido con ID: "+str(id))
        db.session.add(new_accion)
        db.session.commit()
        flash("Compra cancelada correctamente")
        return redirect(url_for('pedidos.arrangement'))
