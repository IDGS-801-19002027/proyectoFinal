import os
from flask import Flask
from flask_login import LoginManager
from flask_security import SQLAlchemyUserDatastore, Security
from flask_sqlalchemy import SQLAlchemy
from .models import db, Role, User, MateriaPrima, Arreglo, DetalleArreglo, Ventas, DetalleVenta, Pedidos, DetallePedido
userDataStore = SQLAlchemyUserDatastore(db, User, Role)

#Inicio de la aplicación
def create_app():
    #Creamos una instancia de la clase Flask
    app = Flask(__name__)
   
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    #Generamos la clave aleatoria de sesión Flask para crear una cookie con la inf. de la sesión
    app.config['SECRET_KEY'] = os.urandom(24)
    #Definimos la ruta a la BD: mysql://user:password@localhost/bd'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/casaflores'
    # We're using PBKDF2 with salt.
    app.config['SECURITY_PASSWORD_HASH'] = 'pbkdf2_sha512'
    #Semilla para el método de encriptado que utiliza flask-security
    app.config['SECURITY_PASSWORD_SALT'] = 'thisissecretsalt'
   
    #Inicializamos y creamos la BD
    db.init_app(app)
    @app.before_first_request
    def create_all():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.index'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Registra el blueprint para las rutas auth de la aplicación (Parte restringida)
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # Registra el blueprint para las partes no auth de la aplicación (Parte publica)
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .arreglos.routes import arreglos
    app.register_blueprint(arreglos)

    from .usuarios.routes import usuarios
    app.register_blueprint(usuarios)

    user_datastore = SQLAlchemyUserDatastore(db, User, Role)

    security = Security(app, user_datastore)

    return app
