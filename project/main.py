from flask import Blueprint, flash, render_template, request
from flask_login import login_required
from flask_security import roles_accepted
from .models import Comentarios
from . import db
main = Blueprint('main', __name__)

@main.route("/")
def inicio():
    return render_template('index.html')

@main.route('/login', methods = ['GET', 'POST'])
def index():
    return render_template('login.html')

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


@main.route('/comentarios')
@login_required
@roles_accepted("Administrador")
def obtenerComentarios():
    comments = Comentarios.query.all()

    return render_template('admin/consultarComentarios.html', comentarios = comments)