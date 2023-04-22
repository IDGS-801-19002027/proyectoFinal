from flask import flash, render_template, redirect
from flask import request
from flask_login import login_user, logout_user, login_required
from flask import url_for
from flask import Blueprint
from flask_security import current_user

from project import forms
from .. import db, main
from ..models import Bitacora, MateriaPrima, DetalleArreglo

materiaPrima = Blueprint('materiaPrima', __name__)

@materiaPrima.route("/listMateria", methods=["GET"])
@login_required
def listMateria():
    formMateria = forms.FormMateria(request.form)
    return render_template("admin/materiaPrima/materia.html", form = formMateria, materias= MateriaPrima.query.all())


@materiaPrima.route("/addMateria", methods=["POST"])
@login_required
def addMateria():
    formMateria = forms.FormMateria(request.form)
    nombreM = formMateria.nombre.data
    nombre = nombreM.upper()
    unidad = formMateria.unidad.data
    cantidad = formMateria.cantidad.data

    # Para encontrar si existe una materia con el mismo nombre
    materia = MateriaPrima.query.filter_by(nombre=nombre).first()
        
    if materia: # Si encuentra una materia prima que ya cuenta con el mismo nombre
        flash("La materia prima ya se encuentra registrada.")
        return redirect(url_for("materiaPrima.listMateria"))
    
    if cantidad < 1:
        flash("No ingrese cantidades menores a 1, por favor.")
        return redirect(url_for("materiaPrima.listMateria"))
    
    # Pasar la unidad de metros a centimetros
    if unidad == 'Piezas':
        cantidad = cantidad
    else :
        cantidad = cantidad * 100

    new_materia = MateriaPrima(nombre = nombre, unidad = unidad, cantidad = cantidad, estatus=1)

    db.session.add(new_materia)
    db.session.commit()

    new_accion = Bitacora(accion = "Nueva materia registrada", descripcion = "El usuario "+current_user.email+" registró la materia prima: "+str(nombre))
    db.session.add(new_accion)
    db.session.commit()
    main.registrarLogs("El usuario "+current_user.nombre+" registró una nueva materia prima "+str(nombre), 'info', 'transaccion')
    flash('Materia registrada correctamente.')
    return redirect(url_for("materiaPrima.listMateria"))


@materiaPrima.route("/updateMateria/<int:id>")
@login_required
def updateMateria(id):
    formMateria = forms.FormMateria(request.form)

    materia = db.session.query(MateriaPrima).filter(
        MateriaPrima.id == int(id)
    ).first()
    db.session.commit()

    formMateria.nombre.data = materia.nombre
    formMateria.unidad.data = materia.unidad
    formMateria.cantidad.data = materia.cantidad
    
    return render_template("admin/materiaPrima/updateMateria.html", form = formMateria, materia = materia)

@materiaPrima.route("/updateMateriaPrima", methods=['POST'])
@login_required
def updateMateriaP():
    id = request.form.get("id")
    formMateria = forms.FormMateria(request.form)
    nombreM = formMateria.nombre.data
    nombre = nombreM.upper()
    unidad = formMateria.unidad.data
    cantidad = formMateria.cantidad.data
 
    # Pasar la unidad de metros a centimetros
    if unidad == 'Piezas':
        cantidad = cantidad
    else :
        cantidad = cantidad * 100

    if(id != 0):
        db.session.query(MateriaPrima).filter(MateriaPrima.id == int(id)).update({"nombre": (nombre), "unidad":(unidad), "cantidad": (cantidad)})
        db.session.commit()
        flash('Materia actualizada correctamente.')
        new_accion = Bitacora(accion = "Materia modificada", descripcion = "El usuario "+current_user.email+" modificó la materia prima: "+str(nombre))
        db.session.add(new_accion)
        db.session.commit()
        main.registrarLogs("El usuario "+current_user.nombre+" modificó la materia prima "+str(nombre), 'info', 'bitacora')
        return redirect(url_for("materiaPrima.listMateria"))
    else:
        flash("El id es inválido")
        return redirect(url_for("materiaPrima.listMateria"))
    
@materiaPrima.route("/deleteMateria/<int:id>")
@login_required
def deleteMateria(id):
    detArreglos = DetalleArreglo.query.all()
    for detArreglo in detArreglos:
        if(id == detArreglo.id_materia_prima):
            materia = db.session.query(MateriaPrima).filter(MateriaPrima.id == DetalleArreglo.id_materia_prima).first()
            if(materia.estatus == True):
                flash("No puedes eliminar una materia prima de un arreglo que se encuentra activo")
                return redirect(url_for("materiaPrima.listMateria"))
    
    db.session.query(MateriaPrima).filter(MateriaPrima.id == int(id)).update({"estatus": 0})
    db.session.commit()
    main.registrarLogs("El usuario "+current_user.nombre+" eliminó la materia prima con ID: "+str(id), 'info', 'transaccion')
    new_accion = Bitacora(accion = "Materia prima eliminada", descripcion = "El usuario "+current_user.email+" eliminó la materia prima con ID: "+str(id))
    db.session.add(new_accion)
    db.session.commit()
    flash('Materia eliminada correctamente.')
    return redirect(url_for("materiaPrima.listMateria"))



