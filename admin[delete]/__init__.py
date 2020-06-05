from flask import Flask
app= Flask(__name__)
import admin
from admin import api
from api import view
from view import mod
# from admin.api.view import mod
app.register_blueprint(mod)