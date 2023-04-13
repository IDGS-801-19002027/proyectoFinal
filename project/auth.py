#Importamos los módulos a usar de flask
from flask import Blueprint, render_template, redirect, url_for, request, flash
#Importamos los módulos de seguridad para las funciones hash
from werkzeug.security import generate_password_hash, check_password_hash

#Importamos el método login_required de flask_security
from flask_security import login_required, current_user
#Importamos los métodos login_user, logout_user flask_security.utils
#########################################################################################
from flask_security.utils import login_user, logout_user, hash_password, encrypt_password
##########################################################################################
#Importamos el modelo del usuario
from . models import User, Role
#Importamos el objeto de la BD y userDataStore desde __init__
from . import db, userDataStore

#Creamos el BluePrint y establecemos que todas estas rutas deben estar dentro de /security para sobre escribir 
# las vistas por omisión de flask-security.
# Por lo que ahora las rutas deberán ser /security/login y security/register
auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        print(email, password)
        remember = True if request.form.get('remember') else False

        # Verifica si hay un usuario creado con el email
        user  = User.query.filter_by(email=email).first()

        # Verifica si el usuario existe
        if not user :
            flash('El usuario y/o contraseña son incorrectos')
            print("Datos no correctos de acceso")
            return redirect(url_for('auth.login'))

        # Se autentica a el usuario
        login_user(user, remember=remember)
        return render_template('index.html')
    
    return render_template('login.html')

@auth.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        lastName = request.form.get('lastName')
        password = request.form.get('password')
        print(email, name, lastName, password)

        #Consultamos si existe un usuario ya registrado con el email.
        user = User.query.filter_by(email=email).first()

        if user: #Si se encontró un usuario, redireccionamos de regreso a la página de registro
            flash('El correo electrónico ya existe')
            return redirect(url_for('auth.register'))

        #Creamos un nuevo usuario con los datos del formulario.
        # Hacemos un hash a la contraseña para que no se guarde la versión de texto sin formato
        #new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))
        new_user = User(nombre=name, 
            email=email, 
            password=generate_password_hash(password, method='sha256'), 
            apellidos=lastName, 
            estatus=1)
        #userDataStore.create_user(
            #name=name, email=email, password=encrypt_password(password)
            #)
        #Añadimos el nuevo usuario a la base de datos.
        db.session.add(new_user)
        db.session.commit()
        #Obtenemos el ultimo registro de usuario
        RecentUser = db.session.query(User).order_by(User.id.desc()).first()
        #Busca el objeto de Rol que coincida con el de cliente
        rolN = db.session.query(Role).filter_by(id=2).first()
        
        #Le agregamos el rol al usuario
        userDataStore.add_role_to_user(RecentUser, rolN)
        db.session.commit()
        print("Usuario con rol registrado")
        flash("Te haz registrado, inicia sesión")

        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth.route('/logout')
@login_required
def logout():
    #Cerramos la sessión
    logout_user()
    return redirect(url_for('main.inicio'))
