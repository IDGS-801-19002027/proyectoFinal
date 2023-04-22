from flask import flash, render_template, redirect
from flask import request
from flask_login import login_user, logout_user, login_required
from flask import url_for
from flask import Blueprint
from flask_security import current_user

from project import forms
from .. import db, main
from ..models import Bitacora, Proveedor

proveedor = Blueprint('proveedor', __name__)

@proveedor.route("/listProveedor", methods=["GET"])
@login_required
def listProveedor():
    formProveedor = forms.FormProveedores(request.form)
    return render_template("admin/proveedor/proveedor.html", form = formProveedor, proveedores= Proveedor.query.all())


@proveedor.route("/addProveedor", methods=["POST"])
@login_required
def addProveedor():
    formProveedor = forms.FormProveedores(request.form)
    nombreP = formProveedor.nombre.data
    nombre = nombreP.upper()
    telefono = formProveedor.telefono.data
    representanteR = formProveedor.representante.data
    representante = representanteR.upper()
    correo = formProveedor.correo.data

    # Para encontrar si existe un proveedor con el mismo nombre
    proveedor = Proveedor.query.filter_by(nombre=nombre).first()
        
    if proveedor: # Si encuentra una materia prima que ya cuenta con el mismo nombre
        flash("El proveedor ingresado ya se encuentra registrado en el sistema.")
        return redirect(url_for("proveedor.listProveedor"))
    
    new_proveedor = Proveedor(nombre = nombre, telefono = telefono, representante = representante, correo = correo, estatus=1)

    db.session.add(new_proveedor)
    db.session.commit()

    new_accion = Bitacora(accion = "Nueva proveedor registrado", descripcion = "El usuario "+current_user.email+" registró el proveedor: "+str(nombre))
    db.session.add(new_accion)
    db.session.commit()
    
    main.registrarLogs("Ha sido registrado un nuevo proveedor por: "+current_user.nombre, 'info', 'bitacora')

    flash('Proveedor registrado correctamente.')
    return redirect(url_for("proveedor.listProveedor"))


@proveedor.route("/updateProveedor/<int:id>")
@login_required
def updateProveedor(id):
    formProveedor = forms.FormProveedores(request.form)
    proveedor = db.session.query(Proveedor).filter(
        Proveedor.id == int(id)
    ).first()
    db.session.commit()

    formProveedor.nombre.data = proveedor.nombre
    formProveedor.telefono.data = proveedor.telefono
    formProveedor.representante.data = proveedor.representante
    formProveedor.correo.data = proveedor.correo
    
    return render_template("admin/proveedor/updateProveedor.html", form = formProveedor, proveedor = proveedor)

@proveedor.route("/updateProveedor", methods=['POST'])
@login_required
def updateProveedorP():
    id = request.form.get("id")
    formProveedor = forms.FormProveedores(request.form)
    nombreP = formProveedor.nombre.data
    nombre = nombreP.upper()
    telefono = formProveedor.telefono.data
    representanteR = formProveedor.representante.data
    representante = representanteR.upper()
    correo = formProveedor.correo.data

    if(id != 0):
        db.session.query(Proveedor).filter(Proveedor.id == int(id)).update({"nombre": (nombre), "representante":(representante), "telefono": (telefono), "correo":(correo)})
        db.session.commit()
        main.registrarLogs("Ha sido modificado un proveedor por: "+current_user.nombre, 'info', 'bitacora')
        
        new_accion = Bitacora(accion = "Proveedor modificado", descripcion = "El usuario "+current_user.email+" modificó el proveedor: "+str(nombre))
        db.session.add(new_accion)
        db.session.commit()
        
        flash('Información del Proveedor actualizada correctamente.')
        return redirect(url_for("proveedor.listProveedor"))
    else:
        flash("El id es inválido")
        return redirect(url_for("proveedor.listProveedor"))
    
@proveedor.route("/deleteProveedor/<int:id>")
@login_required
def deleteProveedor(id):
    
    db.session.query(Proveedor).filter(Proveedor.id == int(id)).update({"estatus": 0})
    db.session.commit()
    main.registrarLogs("Ha sido eliminado el proveedor con ID :"+str(id)+" por: "+current_user.nombre, 'info', 'bitacora')
    new_accion = Bitacora(accion = "Proveedor eliminado", descripcion = "El usuario "+current_user.email+" eliminó el proveedor con ID: "+str(id))
    db.session.add(new_accion)
    db.session.commit()
    
    flash('El Proveedor ahora se encuentra inactivo correctamente.')
    return redirect(url_for("proveedor.listProveedor"))



