# Statement for enabling the development environment
ENV = 'development'
DEBUG = True
TESTING = True
PROPAGATE_EXCEPTIONS = True
# Define the application directory
import os
from pathlib import Path

BASE_DIR =  os.path.dirname(Path(__file__).parent)# os.path.abspath(os.path.dirname(Path(__file__).parent))  

# Define the database - we are working with
# Oracle DB for this example
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
DATABASE_CONNECT_OPTIONS = {}

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED     = True

# Use a secure, unique and absolutely secret key for
# signing the data. 
CSRF_SESSION_KEY = "secret"

# Secret key for signing cookies
SECRET_KEY = "secret"


#CACHE
CACHE_TYPE = "simple"
CACHE_DEFAULT_TIMEOUT = 300

UPLOAD_FOLDER = 'uploads/'


#CELERY config

CELERY_BROKER_URL = 'redis://0.tcp.ngrok.io:13499/0'
CELERY_RESULT_BACKEND = 'redis://0.tcp.ngrok.io:13499/0'



