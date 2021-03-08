from flask import Flask
from flask_bootstrap import Bootstrap
app = Flask(__name__)
app.config.from_pyfile('../earmconfig.py')

Bootstrap(app)

from .converters import RuleConverter
app.url_map.converters['earm_rule'] = RuleConverter

import earm.views
