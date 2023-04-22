from wtforms import Form
from wtforms import SelectField, DecimalField, IntegerField, StringField, EmailField, TextAreaField
from wtforms import validators

'''
Formulario exclusivo para Materia Prima
'''
class FormMateria(Form):
    nombre = StringField('Nombre de la Materia',
                        [
                            validators.DataRequired(message='El campo es obligatorio'),
                            validators.length(min=3, max=50, message='Ingresa un nombre válido.')
                        ])
    cantidad = DecimalField('Cantidad',
                        [
                            validators.DataRequired(message='El campo es obligatorio'), 
                            validators.NumberRange(min=1, max=1000, message="Ingresa una cantidad entre 1 y 1000.")
                        ])
    unidad = SelectField('Unidad', choices = [ 
                                              ('Piezas', 'Piezas'), 
                                              ('Centímetros', 'Metros'),])
    estatus = IntegerField('Estatus')

'''
Formulario exlusivo para Arreglos
'''

class FormArreglo(Form):
    nombre = StringField('Nombre del arreglo',
                        [
                            validators.DataRequired(message='El campo es obligatorio'),
                            validators.length(min=5, max=100, message='Ingresa un nombre válido.')
                        ])
    descripcion = TextAreaField('Descripción del arreglo',
                        [
                            validators.DataRequired(message='El campo es obligatorio'),
                            validators.length(min=5, max=300, message='Ingresa una descripción no mayor a 300 letras.')
                        ])
    precioVenta = IntegerField('Precio de venta',
                        [
                            validators.DataRequired(message='El campo es obligatorio'), 
                            validators.NumberRange(min=1, max=2000, message="Ingresa una cantidad entre 1 y 2000.")
                        ])
    rutaFoto = SelectField('Seleccione la foto', choices = [ 
                                              ('tipo1', 'Arreglo de Tulipanes'), 
                                              ('tipo2', 'Arreglo de Rosas'),
                                              ('tipo3', 'Centro de flores'), 
                                              ('tipo4', 'Ramo de Mano'),
                                              ('tipo5', 'Arreglo de Girasoles'), 
                                              ('tipo6', 'Ramo Gigante de Rosas'),
                                              ('tipo7', 'Arreglo Corona Amarrilla'), 
                                              ('tipo8', 'Arreglo Cojín Clásico'),
                                              ('tipo9', 'Arreglo Caja Imperial Fúnebre'), 
                                              ('tipo10', 'Arreglo Aurora Fúnebre'),
                        ])
    estatus = IntegerField('Estatus')
 
'''
Formulario exclusivo para proveedores
'''
class FormProveedores(Form):
    nombre = StringField('Nombre del Proveedor',
                        [
                            validators.DataRequired(message='El campo es obligatorio'),
                            validators.length(min=3, max=200, message='Ingresa un nombre válido.')
                        ])
    telefono = StringField('Teléfono',
                        [
                            validators.DataRequired(message='El campo es obligatorio'),
                            validators.length(max=10, message='Ingresa un teléfono valido.')
                        ])
    representante = StringField('Nombre del Representante',[
                            validators.DataRequired(message='El campo es obligatorio'),
                            validators.length(min=3, max=100, message='Ingresa un nombre válido.')
                        ])
    correo = EmailField('Correo',
                        [
                            validators.DataRequired(message='El campo es obligatorio'),
                            validators.length(min=10, max=100, message='Ingresa un correo válido.')
                        ])
    estatus = IntegerField('Estatus')

'''
Formulario exclusivo para detalle Arreglo
'''
class FormElaboracion(Form):
    materia = SelectField('Materia prima', choices = [])
    cantidad = DecimalField('Cantidad',
                        [
                            validators.DataRequired(message='El campo es obligatorio'),
                            validators.NumberRange(min=1, max=1000)
                        ])
    
'''
Formulario para compras
'''   
class FormCompra(Form):
    proveedor = SelectField('Proveedor',  choices = [])
    materia = SelectField('Materia prima', choices = [])
    cantidad = IntegerField('Ingrese la cantidad',
                        [
                            validators.DataRequired(message='El campo es obligatorio'),
                            validators.NumberRange(min=1)
                        ])
    costo = DecimalField('Costo por Unidad',
                        [
                            validators.DataRequired(message='El campo es obligatorio'),
                            validators.NumberRange(min=1)
                        ])
    estatus = IntegerField('Estatus')