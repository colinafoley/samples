import sys
activate_this = '/opt/gooclean/gooclean-venv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))
sys.path.insert(0, '/opt/gooclean/')


#sys.stdout = sys.stderr
sys.stderr = sys.stdout

from gooclean import app as application
