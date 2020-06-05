import os 
from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
from flask_caching import Cache
# from flask_socketio import SocketIO
from celery import Celery

api = Flask(__name__, instance_relative_config=True)
CORS(api)



# Load the default configuration
api.config.from_object('config.default')

# Load the configuration from the instance folder
api.config.from_pyfile('config.py')

# Load the environment configuration
api.config.from_object('config.development')
print("base_directory",api.config['BASE_DIR'])

#setup cache
cache = Cache(api)
cache.set("action_metrics",{'dribbling':{'count':0},'kicking':{'count':0},'passing':{'count':0},'running':{'count':0}})
cache.get("action_metrics")

from webapi.views import mod as modules 

api.register_blueprint(modules)


#Socket.io
# socketio = SocketIO(api, cors_allowed_origins="*")


# Celery configuration
api.config['CELERY_BROKER_URL']     = 'redis://0.tcp.ngrok.io:13499/0'
api.config['CELERY_RESULT_BACKEND'] = 'redis://0.tcp.ngrok.io:13499/0'


