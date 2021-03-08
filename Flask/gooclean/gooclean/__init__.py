from flask import Flask
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_orator import Orator

app = Flask(__name__)
app.config.from_pyfile('../goocleanconfig.py')

db = Orator(app)

Bootstrap(app)

nav = Nav()
nav.init_app(app)

import gooclean.views
