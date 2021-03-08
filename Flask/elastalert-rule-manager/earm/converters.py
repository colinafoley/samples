import os, yaml
from werkzeug.routing import BaseConverter
from .models import Rule

#takes a filename and returns/loads a Rule object
from .models import rule_from_file

class RuleConverter(BaseConverter):
    def to_python(self, filename):
        with open(os.path.dirname(os.path.realpath(__file__)) +'/../rules/' + filename) as rule_file:
            return rule_from_file(rule_file, filename)
        return 'woops'

    def to_url(self, filename):
        return filename
