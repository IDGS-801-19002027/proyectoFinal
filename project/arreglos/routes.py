from flask import render_template, redirect
from flask import request
from flask import url_for
from flask import Blueprint
from flask_security import current_user

arreglos = Blueprint('arreglos', __name__)

@arreglos.route('/arreglos', methods = ['GET', 'POST'])
def arrangement():
    return render_template('flower-arrangement.html', user=current_user)

@arreglos.route('/agregar-arreglo', methods = ['GET', 'POST'])
def addArragement():
    return render_template('detailFlower.html', user=current_user)