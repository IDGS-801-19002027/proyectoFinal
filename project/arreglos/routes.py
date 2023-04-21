from flask import flash, render_template, redirect
from flask import request
from flask import url_for
from flask import Blueprint
from flask_login import login_required
from flask_security import current_user

from project import forms
from .. import db, main
from ..models import Arreglo, Bitacora, MateriaPrima, DetalleArreglo

arreglos = Blueprint('arreglos', __name__)

@arreglos.route('/arreglos', methods = ['GET', 'POST'])
def arrangement():
    return render_template('flower-arrangement.html', user=current_user)

@arreglos.route('/arreglos2', methods = ['GET'])
def arreglos2():
    arreglos = Arreglo.query.all()
    print(arreglos)
    return render_template('flower-arrangement.html', arreglos = arreglos)

@arreglos.route('/agregar-arreglo', methods = ['GET', 'POST'])
def addArragement():
    return render_template('detailFlower.html', user=current_user)

######### Admin - Arreglos #########
@arreglos.route("/listArreglo", methods=["GET"])
@login_required
def listArreglo():
    formArreglo = forms.FormArreglo(request.form)
    return render_template("admin/arreglo/arreglo.html", form = formArreglo, arreglos= Arreglo.query.all())

@arreglos.route("/addArreglo", methods=["POST"])
@login_required
def addArreglo():
    formArreglo = forms.FormArreglo(request.form)
    nombreM = formArreglo.nombre.data
    nombre = nombreM.upper()
    rutaFoto = formArreglo.rutaFoto.data
    descripcion = formArreglo.descripcion.data
    precioVenta = formArreglo.precioVenta.data

    # Para encontrar si existe un producto con el mismo nombre
    arreglo = Arreglo.query.filter_by(nombre=nombre).first()
        
    if arreglo: # Si encuentra una materia prima que ya cuenta con el mismo nombre
        flash("El arreglo a registrar ya se encuentra en el sistema.")
        return redirect(url_for("arreglos.listArreglo"))
    
    new_arreglo = Arreglo(nombre = nombre, descripcion = descripcion, rutaFoto = rutaFoto, precioVenta = precioVenta, estatus=1)

    db.session.add(new_arreglo)
    db.session.commit()
    main.registrarLogs("El usuario "+current_user.nombre+" registró un nuevo arreglo "+str(nombre), 'info', 'bitacora')
    new_accion = Bitacora(accion = "Nueva arreglo registrado", descripcion = "El usuario "+current_user.email+" registró el arreglo: "+str(nombre))
    db.session.add(new_accion)
    db.session.commit()
    
    flash('Producto registrado correctamente.')
    
    return redirect(url_for("arreglos.listArreglo"))

@arreglos.route("/updateArregloSeleccionado/<int:id>")
@login_required
def updateArreglo(id):
    formArreglo = forms.FormArreglo(request.form)

    arreglo = db.session.query(Arreglo).filter(
        Arreglo.id == int(id)
    ).first()
    db.session.commit()

    formArreglo.nombre.data = arreglo.nombre
    formArreglo.descripcion.data = arreglo.descripcion
    formArreglo.rutaFoto.data = arreglo.rutaFoto
    formArreglo.precioVenta.data = arreglo.precioVenta
    
    return render_template("admin/arreglo/updateArreglo.html", form = formArreglo, arreglo = arreglo)

@arreglos.route("/updateArreglo", methods=['POST'])
@login_required
def updateMateriaP():
    id = request.form.get("id")
    formArreglo = forms.FormArreglo(request.form)
    nombreM = formArreglo.nombre.data
    nombre = nombreM.upper()
    rutaFoto = formArreglo.rutaFoto.data
    descripcion = formArreglo.descripcion.data
    precioVenta = formArreglo.precioVenta.data

    if(id != 0):
        db.session.query(Arreglo).filter(Arreglo.id == int(id)).update({"nombre": (nombre), "descripcion":(descripcion), "rutaFoto":(rutaFoto), "precioVenta": (precioVenta)})
        db.session.commit()
        main.registrarLogs("El usuario "+current_user.nombre+" actualizó el arreglo "+str(nombre), 'info', 'bitacora')
        new_accion = Bitacora(accion = "Arreglo modificado", descripcion = "El usuario "+current_user.email+" modificó el arreglo: "+str(nombre))
        db.session.add(new_accion)
        db.session.commit()
        
        flash('Arreglo actualizado correctamente.')
        return redirect(url_for("arreglos.listArreglo"))
    else:
        flash("El id es inválido")
        return redirect(url_for("arreglos.listArreglo"))

@arreglos.route("/deleteArreglo/<int:id>")
@login_required
def deleteArreglo(id):
    
    db.session.query(Arreglo).filter(Arreglo.id == int(id)).update({"estatus": 0})
    db.session.commit()
    main.registrarLogs("El usuario "+current_user.nombre+" eliminó el arreglo con ID: "+str(id), 'info', 'transaccion')
    new_accion = Bitacora(accion = "Arreglo eliminado", descripcion = "El usuario "+current_user.email+" eliminó el arreglo floral con ID: "+str(id))
    db.session.add(new_accion)
    db.session.commit()
    
    flash("El arreglo seleccionado ha sido eliminado correctamente.")
    return redirect(url_for("arreglos.listArreglo"))

######### Admin - Detalle arreglo #########
@arreglos.route('/elaboracion')
@login_required
def elaboracion():
    formElaboracion = forms.FormElaboracion()

    arreglo = db.session.query(Arreglo).order_by(Arreglo.id.desc()).first()
    idArreglo = arreglo.id
    
    detArreglo = db.session.query(DetalleArreglo).filter(DetalleArreglo.id_arreglo == int(idArreglo))
    
    materiasPrimas = []
    for materia in db.session.query(MateriaPrima).all():
        if materia.estatus == 1:
            materiasPrimas.append(materia.nombre)
       
    db.session.close()
    formElaboracion.materia.choices = materiasPrimas
    materias = MateriaPrima.query.all()
    return render_template('admin/arreglo/elaboracion.html', form = formElaboracion, arreglo = arreglo, detArreglo = detArreglo, materias = materias)

@arreglos.route('/addElabArreglo', methods=["POST"])
@login_required
def addElabProd():
    formElaboracion = forms.FormElaboracion(request.form, request.data)
    id_arreglo = int(request.form.get("id_arreglo"))
    nombre_materia = formElaboracion.materia.data
    cantidad = formElaboracion.cantidad.data
    
    materia = MateriaPrima.query.filter_by(nombre = nombre_materia).first()
    
    new_elabArreglo = DetalleArreglo(id_arreglo = id_arreglo, id_materia_prima= materia.id, cantidad=cantidad)
    
    db.session.add(new_elabArreglo)
    db.session.commit()
    
    return redirect(url_for('arreglos.elaboracion'))

@arreglos.route("/finishElabArreglo/<int:id>")
@login_required
def finishElabArreglo(id):
    detArreglo = db.session.query(DetalleArreglo).filter(DetalleArreglo.id_arreglo == int(id)).all()
    n=0
    for detalle in detArreglo:
        n+=1
    if(n<2):
        flash("Atención, queda poca materia prima de este insumo")
        return redirect(url_for("arreglos.elaboracion"))
    else:
        return redirect(url_for("arreglos.listArreglo"))
'''
@arreglos.route("/detArreglo", methods=["GET"])
@login_required
def detArreglo():
    arreglos = db.session.query(Arreglo).all()
    detArreglo = DetalleArreglo.query.all()
    return render_template("admin/detArreglo.html", arreglos = arreglos, detArreglo = detArreglo )
'''
