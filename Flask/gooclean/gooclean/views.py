from os import listdir
from functools import wraps
from subprocess import Popen
from tempfile import mkstemp
from flask import render_template, flash, url_for, request, redirect, abort
from flask_nav.elements import *
from . import app, nav
from .models import User
from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectMultipleField, StringField, widgets
from flask_paginate import Pagination, get_page_args

def check_auth(username):
    """This function is called to check if a username /
    password combination is valid.
    """
    authorized_users = [REDACTED]
    return username in authorized_users

def requires_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username):
            abort(403)
        return f(*args, **kwargs)
    return decorated

@nav.navigation('top_nav')
def top_nav():
    items = [View('Home', 'index')]
    if check_auth(request.authorization.username):
        items.append(View('Admin', 'admin'))
    return Navbar('GooClean', *items)

def get_already_claimed_files_for(email):
    user = email.strip('@REDACTED')

    claim_files = [f for f in listdir('/tmp') if ('gooclean' in f and user in f)]
    fileids = []
    for f in claim_files:
        fh = open('/tmp/' + f)
        for line in fh:
            fileids.append(line.split(" ")[2].rstrip())

    return fileids

def claim(email):
    user = User.where('email', email).first()
    xref_options = []
    xref_owners = {}
    count = 0
    already_claimed_files = get_already_claimed_files_for(email)
    if user:
        xrefs = user.xrefs
        if xrefs:
            for xref in xrefs:
                if xref.file and (xref.file.fileid not in already_claimed_files):
                    xref_options.append([xref.file.fileid, xref.file.title])
                    xref_owners[xref.file.fileid] = xref.file.owner
            count = len(xref_options)

    class ClaimForm(FlaskForm):
        files = SelectMultipleField('Files', choices=xref_options, option_widget=widgets.CheckboxInput())
        claim = SubmitField('Claim')

    form = ClaimForm()
    if form.validate_on_submit():
        filelist = request.form.getlist('files')
        if filelist:
            count = len(filelist)
            fp, path = mkstemp(prefix='gooclean_' + email.strip('@REDACTED') + '_' + str(count) + '_')
            with open(path, 'w') as f:
                for fileid in filelist:
                    f.write(xref_owners[fileid] + ' ' + email + ' ' + fileid + '\n')
            cmd = [REDACTED]
            p = Popen(cmd,shell=False,stdin=None,stdout=None,stderr=None,close_fds=True,)
            flash('Your claims have been submitted for processing.')
            if 'admin' in request.path:
                return redirect(url_for('admin_claim', user=email))
            else:
                return redirect(url_for('index'))

    return render_template('index.html', user=email, form=form, xref_owners=xref_owners, count=count)

@app.route('/', methods=['GET', 'POST'])
def index():
    return claim(request.authorization.username + '@REDACTED')


@app.route('/admin/', methods=['GET', 'POST'])
@requires_admin
def admin():
    form = UserSelectForm()
    if form.validate_on_submit():
        return redirect(url_for('admin_claim', user=request.form['user']))
    return render_template('admin.html', form=form)

class UserSelectForm(FlaskForm):
    user = StringField('User', description='Enter a user in the form of REDACTED')
    submit = SubmitField('Submit')

@app.route('/admin/<user>/', methods=['GET', 'POST'])
@requires_admin
def admin_claim(user):
    flash('ADMIN: You are impersonating ' + user, 'error')
    return claim(user);
