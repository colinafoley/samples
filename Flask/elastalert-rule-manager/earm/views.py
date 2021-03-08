from functools import wraps
from flask import Response, url_for, render_template, request, redirect, flash
from datetime import datetime
import os, glob, yaml
from . import app
from .models import Rule, rule_from_file, rchop
from .forms import RuleForm, RuleDeleteForm, CrazyForm

def authenticate():
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth:
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/')
@requires_auth
def index():
    rules = get_rules(state="active")
    disabled_rules = get_rules(state="disabled")
    return render_template('index.html', rules=rules, disabled_rules=disabled_rules)

@app.route('/rule/add', methods=['POST', 'GET'])
@requires_auth
def rule_add():
    form = RuleForm()
    if form.validate_on_submit():
        rule = Rule(
            name=request.form['name'],
            query=request.form['query'],
            alert=request.form['alert'],
            index=request.form['index'],
            es_host=request.form['es_host'],
            es_port=int(request.form['es_port']),
            rule_type=request.form['rule_type'],
            email=request.form['email'].splitlines(),
            email_reply_to=request.form['email_reply_to'],
            smtp_host=request.form['smtp_host'],
            author=request.authorization.username,
            created=datetime.now().isoformat(),
            modifications=[{datetime.now().isoformat(): request.authorization.username}]
        )
        rule.save()
        flash('Rule added', category="success")
        return redirect(url_for('index'))
    return render_template('add_rule.html', form=form)

@app.route('/rule/add/crazy', methods=['POST', 'GET'])
@requires_auth
def crazy_add():
    form = CrazyForm()
    if form.validate_on_submit():
        yaml_string = request.form['yaml']
        rule_yaml = yaml.safe_load(yaml_string)
        rule_yaml['author'] = request.authorization.username
        rule_yaml['created'] = datetime.now().isoformat()
        rule_yaml['modifications'] = [{datetime.now().isoformat(): request.authorization.username}]
        rule = Rule(**rule_yaml)
        rule.save()
        flash('Crazy added', category="warning")
        return redirect(url_for('index'))
    return render_template('add_rule.html', form=form)

@app.route('/rule/<earm_rule:rule>')
@requires_auth
def show_rule(rule):
    return render_template('show_rule.html', rule=rule.render())

@app.route('/rule/<earm_rule:rule>/edit', methods=["POST", "GET"])
@requires_auth
def edit_rule(rule):
    try:
        rule.rule_type
        if (rule.rule_type == 'any'):
            form = RuleForm(obj=rule)
            if form.validate_on_submit():
                form.populate_obj(rule)
                rule.email = request.form['email'].splitlines()
                rule.es_port = int(rule.es_port)
                #pack in new modification date
                rule.modifications.append({
                    datetime.now().isoformat():
                    request.authorization.username
                })
                rule.save()
                flash('Rule overwritten', category="success")
                return redirect(url_for('index'))
            form.email.data = "\n".join(form.email.data)
        return render_template('add_rule.html', form=form)
    except:
        form = CrazyForm()
        if form.validate_on_submit():
            yaml_string = request.form['yaml']
            rule_yaml = yaml.safe_load(yaml_string)
            #pack in new modification date
            rule_yaml['modifications'].append({
                datetime.now().isoformat(): request.authorization.username
            })
            rule = Rule(**rule_yaml)
            rule.save()
            flash('Crazy edited', category="warning")
            return redirect(url_for('index'))
        form.yaml.data = rule.render()
        return render_template('add_rule.html', form=form)

@app.route('/rule/<earm_rule:rule>/delete', methods=["POST", "GET"])
@requires_auth
def del_rule(rule):
    form = RuleDeleteForm()
    if form.validate_on_submit():
        os.remove(os.path.dirname(os.path.realpath(__file__)) + "/../rules/" + rule.filename)
        os.remove(os.path.dirname(os.path.realpath(__file__)) + "/../rules/" + rchop(rule.filename.replace(".yaml", ".meta"), ".disabled"))
        flash('Rule deleted', category="warning")
        return redirect(url_for('index'))
    return show_rule(rule) + render_template('del_rule.html', form=form)

@app.route('/rule/<earm_rule:rule>/test')
@requires_auth
def test_rule(rule):
    return render_template('show_rule.html', rule=rule.test())

def get_rules(state="active"):
    #get the yaml rules
    if (state == "active"):
        pattern = "*.yaml"
    else:
        pattern = "*.disabled"
    rules = []
    for path in glob.glob(os.path.dirname(os.path.realpath(__file__)) + "/../rules/" + pattern):
        filename = os.path.basename(path)
        with open(path) as rule_file:
            rules.append(rule_from_file(rule_file, filename))
    return rules

@app.route('/rule/<earm_rule:rule>/enable')
@requires_auth
def enable(rule):
    os.rename(
        os.path.dirname(os.path.realpath(__file__)) + "/../rules/" + rule.filename,
        os.path.dirname(os.path.realpath(__file__)) + "/../rules/" + rule.filename.replace(".disabled", "")
    )
    return redirect(url_for('index'))

@app.route('/rule/<earm_rule:rule>/disable')
@requires_auth
def disable(rule):
    os.rename(
        os.path.dirname(os.path.realpath(__file__)) + "/../rules/" + rule.filename,
        os.path.dirname(os.path.realpath(__file__)) + "/../rules/" + rule.filename + ".disabled"
    )
    return redirect(url_for('index'))

@app.route('/rule/<earm_rule:rule>/meta')
@requires_auth
def show_meta(rule):
    return render_template('show_rule.html', rule=rule.render(meta=True))
