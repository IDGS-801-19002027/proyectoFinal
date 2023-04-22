from flask import render_template, redirect
from flask import request
from flask import url_for
from flask import Blueprint
from flask_security import current_user

from project.models import Arreglo

flowers = Blueprint('flowers', __name__)

@flowers.route('/arrangement', methods = ['GET', 'POST'])
def arrangement():
    arreglos = Arreglo.query.all()
    return render_template('cliente/detArreglo.html', arreglos = arreglos)

@flowers.route('/add-arragement', methods = ['GET', 'POST'])
def addArragement():
    return render_template('detailFlower.html', user=current_user)