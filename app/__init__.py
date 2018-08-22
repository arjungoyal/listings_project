from flask import Flask
from config import Config
from flask_bootstrap import Bootstrap

app_var  = Flask(__name__)
app_var.config.from_object(Config)
bootstrap = Bootstrap(app_var)


from app import routes
