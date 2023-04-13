from flask import render_template, redirect
from flask import request
from sqlalchemy import update
from werkzeug.security import generate_password_hash
from flask import url_for
from flask import Blueprint
from flask_login import login_required
from flask_security import roles_accepted
from ..models import User, Role, users_roles
from .. import db, userDataStore

usuarios = Blueprint('usuarios', __name__)

@usuarios.route('/usuarios', methods=['GET', 'POST'])
@login_required
@roles_accepted("Administrador")
def getAllUsers():
    usuarios = db.session.query(User).filter_by(estatus=1).all()

    if request.method =='POST':
        st = request.form.get("estatus")
        usuarios =  db.session.query(User).filter_by(estatus=st).all()
        render_template('admin/usuarios.html', usuarios=usuarios)
        
    return render_template('admin/usuarios.html', usuarios=usuarios)

@usuarios.route('/agregar-usuario', methods=['GET', 'POST'])
@login_required
@roles_accepted("Administrador")
def addUsers():

    if request.method=='POST':
        name = request.form.get('name')
        lastName = request.form.get('lastName')
        email = request.form.get('email')
        password = request.form.get('password')
        rol = request.form.get('rol')

        new_user = User(nombre=name, 
                email=email, 
                password=generate_password_hash(password, method='sha256'), 
                apellidos=lastName, 
                estatus=1)
        
        db.session.add(new_user)
        db.session.commit()
        #Obtenemos el ultimo registro de usuario
        RecentUser = db.session.query(User).order_by(User.id.desc()).first()
        #Busca el objeto de Rol que coincida con el seleccionado
        rolN = db.session.query(Role).filter_by(id=rol).first()
        
        #Le agregamos el rol al usuario
        userDataStore.add_role_to_user(RecentUser, rolN)
        db.session.commit()

        return redirect(url_for('usuarios.getAllUsers'))

    return render_template('admin/agregarUsuario.html')

@usuarios.route('/modificar-usuario', methods=['GET', 'POST'])
@login_required
@roles_accepted("Administrador")
def updateUsers():
    id = request.args.get('id')
    usuario = db.session.query(User).filter(User.id == id).first()

    if request.method=='POST':
        id = request.form.get('idUsuario')
        modifUser = db.session.query(User).filter(User.id == id).first()
        modifUser.nombre = request.form.get('nombre')
        modifUser.apellidos = request.form.get('apellidos')
        modifUser.email = request.form.get('email')
        password = request.form.get('password')
        modifUser.password = generate_password_hash(password, method='sha256')
        rol = request.form.get('rol')

        db.session.add(modifUser)
        db.session.commit()
        #Para actualizar el rol, su instancia la tabla users_roles
        #Consulta para actualizar tomando como referencia el id que tomo como parametro y cambiando el valor del rol
        query = update(users_roles).where(users_roles.columns.get('userId') == id).values(roleId=rol)
        #Ejecuta la consulta
        db.session.execute(query)
        #Guarda los cambios
        db.session.commit()

        return redirect(url_for('usuarios.getAllUsers'))
    
    return render_template('admin/actualizarUsuario.html', usuario=usuario)

@usuarios.route('/eliminar-usuario', methods=['GET', 'POST'])
@login_required
@roles_accepted("Administrador")
def deleteUsers():
    id = request.args.get('id')
    usuario = db.session.query(User).filter(User.id == id).first()

    if request.method=='POST':
        id = request.args.get('id')
        usuarioD = db.session.query(User).filter(User.id == id).first()

        usuarioD.estatus = 0

        db.session.add(usuarioD)
        db.session.commit()
        return redirect(url_for('usuarios.getAllUsers'))
    
    return render_template('admin/eliminarUsuario.html', usuario=usuario)

@usuarios.route('/reactivar-usuario', methods=['GET', 'POST'])
@login_required
@roles_accepted("Administrador")
def reactivateUsers():
    id = request.args.get('id')
    usuario = db.session.query(User).filter(User.id == id).first()

    if request.method=='POST':
        id = request.args.get('id')
        usuarioR = db.session.query(User).filter(User.id == id).first()

        usuarioR.estatus = 1

        db.session.add(usuarioR)
        db.session.commit()
        return redirect(url_for('usuarios.getAllUsers'))
    
    return render_template('admin/reactivarUsuario.html', usuario=usuario)