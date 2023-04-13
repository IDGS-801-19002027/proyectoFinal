from flask import render_template, redirect
from flask import request
from flask import url_for
from flask import Blueprint
from flask_security import current_user

ventas = Blueprint('ventas', __name__)