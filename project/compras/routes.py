from datetime import datetime
from flask import flash, render_template, redirect
from flask import request
from flask_login import login_user, logout_user, login_required
from flask import url_for
from flask import Blueprint
from flask_security import current_user

from project import forms
from .. import db, main
from ..models import Compra, DetalleCompra, MateriaPrima, Proveedor, User, Bitacora

compra = Blueprint('compra', __name__)

@compra.route("/listCompra", methods=["GET"])
@login_required
def listCompra():
    formCompra = forms.FormCompra(request.form)
    proveedores = []
    #materiasPrimas = []
    materiasPrimas = [(materia.id, materia.nombre) for materia in db.session.query(MateriaPrima).filter(MateriaPrima.estatus == True).all()]

    #for materia in db.session.query(MateriaPrima):
        #if(materia.estatus == True):
            #materiasPrimas.append(materia.nombre)
       
    for proveedor in db.session.query(Proveedor):
        if(proveedor.estatus == True):
            proveedores.append(proveedor.nombre)

    if proveedores == '':
        flash("Para hacer una compra debe primero registrar proveedores.")

    compras = db.session.query(Compra, User.nombre.label('nombre_usuario'), Proveedor.nombre.label('nombre_proveedor')).join(
    User).join(Proveedor).all()
    
    detCompras = db.session.query(DetalleCompra, MateriaPrima.nombre).join(MateriaPrima).filter(DetalleCompra.idMateria == MateriaPrima.id)
    
    db.session.close()
    formCompra.materia.choices = materiasPrimas
    formCompra.proveedor.choices = proveedores
    print(materiasPrimas)
    return render_template('admin/compra/compra.html', form = formCompra, compras = compras, detCompras = detCompras, materias = materiasPrimas)

@compra.route("/addCompra", methods=["POST"])
@login_required
def addCompra():
    # Agregar los datos de la compra
    formCompra = forms.FormCompra(request.form, request.data)
    nameProveedor = formCompra.proveedor.data
    proveedor = Proveedor.query.filter_by(nombre = nameProveedor).first()

    # Obtener los datos de las materias primas seleccionadas
    materias = request.form.getlist("materia[]")
    cantidades = request.form.getlist("cantidad[]")
    costos = request.form.getlist("costo[]")

    if len(materias) == '' or len(cantidades) == '' or len(costos) == '':
        flash("Debe completar el detalle de compra antes de finalizar la compra.")
        return redirect(url_for("compra.listCompra"))
    
    else :
        new_compra = Compra(idUsuario=current_user.id, idProveedor=proveedor.id, fecha=datetime.today(), estatus=1)
        db.session.add(new_compra)
        db.session.commit()
        main.registrarLogs("El usuario "+current_user.nombre+" registró una nueva compra al proveedor "+str(nameProveedor), 'info', 'transaccion')
        new_accion = Bitacora(accion = "Nueva compra registrada", descripcion = "El usuario "+current_user.email+" registró una nueva compra al proveedor: "+str(nameProveedor))
        db.session.add(new_accion)
        db.session.commit()
    
        compra = db.session.query(Compra).order_by(Compra.idCompra.desc()).first()

        # Iterar sobre las listas de materias primas, cantidades y costos para registrar el detalle de compra
        for i in range(len(materias)):
            nameMateria = materias[i]
            cantidad = int(cantidades[i])

            precioU = float(costos[i])
            aux_cantidad = cantidad

            materia = MateriaPrima.query.filter_by(nombre=nameMateria).first()

            if materia.unidad != "Piezas":
                cantidad = cantidad * 100

            cantidad += materia.cantidad

            costo = precioU * aux_cantidad

            db.session.query(MateriaPrima).filter(MateriaPrima.id == int(materia.id)).update({"cantidad": (cantidad)})
            db.session.commit()

            new_detCompra = DetalleCompra(idCompra=compra.idCompra, idMateria=materia.id, cantidad=aux_cantidad, costo=costo)
            db.session.add(new_detCompra)
            db.session.commit()

        flash("Compra registrada correctamente")
        return redirect(url_for("compra.listCompra"))

@compra.route("/cancelCompra/<int:id>")
@login_required
def cancelCompra(id):
    detalles = DetalleCompra.query.filter_by(idCompra=id).all()
    for detalle in detalles:
        materia_prima = MateriaPrima.query.get(detalle.idMateria)
        materia_prima.cantidad -= detalle.cantidad

    db.session.commit()
    main.registrarLogs("El usuario "+current_user.nombre+" canceló una compra con ID: "+str(id), 'info', 'transaccion')

    db.session.query(Compra).filter(Compra.idCompra == int(id)).update({"estatus": 0})
    db.session.commit()

    new_accion = Bitacora(accion = "Compra cancelada", descripcion = "El usuario "+current_user.email+" ha cancelado la compra con ID: "+str(id))
    db.session.add(new_accion)
    db.session.commit()
    
    flash("Compra cancelada correctamente.")
    return redirect(url_for("compra.listCompra"))

