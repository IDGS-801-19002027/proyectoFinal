from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_security import RoleMixin

db = SQLAlchemy()

users_roles = db.Table( 'usuario_roles',
 db.Column('userId', db.Integer, db.ForeignKey('usuario.id')),
 db.Column('roleId', db.Integer, db.ForeignKey('roles.id'))
)

class User(db.Model,UserMixin):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    estatus = db.Column(db.Integer, nullable=False)
    roles= db.relationship('Role',
                           secondary= users_roles,
                           backref= db.backref('users', lazy= 'dynamic')
                           )
    detalle_pedido = db.relationship('DetallePedido', backref=db.backref('detalle_pedido'))
    #usuario_ventas = db.relationship('Ventas', backref=db.backref('user'))
    #usuario_pedidos = db.relationship('Pedidos', backref=db.backref('user'))
    def has_role(self, *args):
        return set(args).issubset({roles.name for roles in self.roles})

class Role (RoleMixin, db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(50))

class Proveedor (db.Model):
    __tablename__ = 'proveedor'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200))
    telefono = db.Column(db.String(10))
    representante = db.Column(db.String(100))
    correo = db.Column(db.String(100))
    estatus = db.Column(db.Integer)

class MateriaPrima (db.Model):
    __tablename__ = 'materiaPrima'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50))
    unidad = db.Column(db.String(30))
    cantidad = db.Column(db.Integer)
    estatus = db.Column(db.Integer)
    detalle_arreglos = db.relationship('DetalleArreglo', backref=db.backref('materia_prima', 
                                                                            lazy='select'))
class Arreglo (db.Model):
    __tablename__ = 'arreglo'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    descripcion = db.Column(db.String(300))
    precioVenta = db.Column(db.Integer)
    rutaFoto = db.Column(db.String(50))
    estatus = db.Column(db.Integer)
    detalle_arreglos = db.relationship('DetalleArreglo', backref=db.backref('arreglo', lazy='select'))

class DetalleArreglo (db.Model):
    __tablename__ = 'detalleArreglo'
    id = db.Column(db.Integer, primary_key=True)
    cantidad = db.Column(db.Integer)
    id_arreglo = db.Column(db.Integer, db.ForeignKey('arreglo.id'))
    id_materia_prima = db.Column(db.Integer, db.ForeignKey('materiaPrima.id'))

class Compra (db.Model):
    __tablename__ = "compra"
    idCompra = db.Column(db.Integer, primary_key=True)
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    idProveedor = db.Column(db.Integer, db.ForeignKey('proveedor.id'))
    fecha = db.Column(db.Date)
    estatus = db.Column(db.Integer)
    
    usuario = db.relationship('User')
    proveedor = db.relationship('Proveedor')

class DetalleCompra(db.Model):
    __tablename__ = "detalleCompra"
    idDetCompra = db.Column(db.Integer, primary_key=True)
    idCompra = db.Column(db.Integer, db.ForeignKey('compra.idCompra'))
    idMateria = db.Column(db.Integer, db.ForeignKey('materiaPrima.id'))
    cantidad = db.Column(db.Float, nullable = False)
    costo = db.Column(db.Float, nullable = False)
    
    compra = db.relationship('Compra')
    materiaPrima = db.relationship('MateriaPrima')

class Comentarios (db.Model):
    __tablename__ = 'comentarios'
    id = db.Column(db.Integer, primary_key=True)
    correo = db.Column(db.String(30))
    mensaje = db.Column(db.String(200))

class Ventas (db.Model):
    __tablename__ = 'ventas'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.String(50))
    total = db.Column(db.Double)
    estatus = db.Column(db.Integer)
    #id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    detalle_ventas = db.relationship('DetalleVenta', backref=db.backref('detalleVenta'))

class DetalleVenta(db.Model):
    __tablename__ = 'detalleVenta'
    id = db.Column(db.Integer, primary_key=True)
    cantidad = db.Column(db.Integer)
    subtotal = db.Column(db.Double)
    id_arreglo = db.Column(db.Integer, db.ForeignKey('arreglo.id'))
    id_venta = db.Column(db.Integer, db.ForeignKey('ventas.id'))

class Pedidos (db.Model):
    __tablename__ = 'pedidos'
    id = db.Column(db.Integer, primary_key=True)
    fechaPedido = db.Column(db.String(50))
    total = db.Column(db.Double)
    estatus = db.Column(db.Integer)
    #id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    pedidos_ventas = db.relationship('DetallePedido', backref=db.backref('detallePedido'))

class DetallePedido(db.Model):
    __tablename__ = 'detallePedido'
    id = db.Column(db.Integer, primary_key=True)
    cantidad = db.Column(db.Integer)
    subtotal = db.Column(db.Double)
    id_arreglo = db.Column(db.Integer, db.ForeignKey('arreglo.id'))
    id_pedido = db.Column(db.Integer, db.ForeignKey('pedidos.id'))
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'))

class Bitacora(db.Model):
    __tablename__ = 'bitacora'
    id = db.Column(db.Integer, primary_key=True)
    accion = db.Column(db.String(100))
    descripcion = db.Column(db.String(300))