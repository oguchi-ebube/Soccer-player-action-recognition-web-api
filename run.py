from webapi import api
from flask_ngrok import run_with_ngrok
from flask import Flask

run_with_ngrok(api)
api.run()
  
  

#starting celery
# @celery.task()

# api.run(api,host="localhost", debug=True)