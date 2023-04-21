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

from . import main
 
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

        # Verifica si hay un usuario creado con el mismo correo
        user  = User.query.filter_by(email=email).first()

        # Tomamos el password proporcionado por el usuario, lo hasheamos y lo comparamos con el  password
        if not user or not check_password_hash(user.password, password) :
            flash('El usuario y/o contraseña son incorrectos.')
            print("Datos de acceso no correctos.")
            main.registrarLogs("Intento de logueo con datos incorrectos con el correo "+email, 'warn', 'bitacora')
            return redirect(url_for('auth.login'))
        
        # Verificar estatus
        if(user.estatus == 0):
            flash("El usuario esta inhabilitado, ingrese con otro usuario.")
            main.registrarLogs("Intento de logueo con usuario inactivo", 'warn', 'bitacora')
            return redirect(url_for("auth.login"))

        # Si llegamos aquí, el usuario tiene datos correctos, creamos una sesion y logueamos al usuario
        login_user(user, remember=remember)
        main.registrarLogs('Inicio sesion el usuario '+user.nombre, 'info', 'bitacora')
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
            flash('El correo electrónico ya existe.')
            main.registrarLogs("Intento de registro con correo ya existente. Correo: "+email, 'error', 'error')
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
        main.registrarLogs('Se registró un nuevo cliente. Nombre: '+str(new_user.nombre)+' '+str(new_user.apellidos)+', Correo: '+str(new_user.email), 'info', 'bitacora')
        flash("Te has registrado con éxito, inicia sesión.")

        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth.route('/logout')
@login_required
def logout():
    main.registrarLogs('Sesión finalizada por el usuario '+current_user.nombre, 'info', 'bitacora')
    #Cerramos la sessión
    logout_user()
    return redirect(url_for('main.inicio'))
