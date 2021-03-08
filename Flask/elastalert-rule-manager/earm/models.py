import yaml
import string
import unicodedata
import uuid
import os
import subprocess
from datetime import datetime

def rchop(thestring, ending):
    if thestring.endswith(ending):
        return thestring[:-len(ending)]
    return thestring

class Rule(yaml.YAMLObject):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
            if (key == 'type'):
                setattr(self, 'rule_type', value)

        try:
            self.name
        except AttributeError:
            self.name = 'Misconfigured rule file; MUST DELETE'

        try:
            self.filename
        except AttributeError:
            self.filename = self.clean_name(self.name) + "_" + str(uuid.uuid4()) + ".yaml.disabled"

    def __repr__(self):
        return "%r" % self.__dict__

    def dumpit(self):
        try:
            self.rule_type
            if (self.rule_type == 'any'):
                return {'name': self.name,
                        'filter': [{'query': {'query_string': {'query': self.query}}}],
                        'index': self.index,
                        'es_host': self.es_host,
                        'es_port': self.es_port,
                        'email': self.email,
                        'type': self.rule_type,
                        'alert': self.alert,
                        'smtp_host': self.smtp_host,
                        'email_reply_to': self.email_reply_to
                       };
            return self.__dict__
        except:
            return self.__dict__

    def dumpmeta(self):
        try:
            self.author
            self.created
            self.modifications
            return {'author': self.author,
                    'created': self.created,
                    'modifications': self.modifications
                    };
        except:
            return {'error': 'metadata missing'}

    def save(self):
        with open(os.path.dirname(os.path.realpath(__file__)) + "/../rules/" + self.filename, 'w') as target:
            target.write(yaml.safe_dump(self.dumpit(), indent=4, allow_unicode=True, default_flow_style=False))

        with open(os.path.dirname(os.path.realpath(__file__)) + "/../rules/" + rchop(self.filename.replace('.yaml','.meta'), ".disabled"), 'w') as target:
            target.write(yaml.safe_dump(self.dumpmeta(), indent=4, allow_unicode=True, default_flow_style=False))

    def clean_name(self, filename):
        validFilenameChars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        cleanedFilename = unicodedata.normalize('NFKD', unicode(filename)).encode('ASCII', 'ignore')
        cleanedFilename = cleanedFilename.replace(' ','_')
        return ''.join(c for c in cleanedFilename if c in validFilenameChars)

    def render(self, format="string", meta=False):
        path = os.path.dirname(os.path.realpath(__file__)) + "/../rules/" + self.filename
        if meta:
            path = rchop(path.replace(".yaml", ".meta"), ".disabled")

        output = ""
        with open(path) as rule_file:
            for line in rule_file:
                output += line
        return output

    def test(self):
        path = os.path.dirname(os.path.realpath(__file__)) + "/../rules/" + self.filename
        try:
            return subprocess.check_output('elastalert-test-rule ' + path + ' 2>&1', shell=True)
        except subprocess.CalledProcessError as e:
            return e.output

def meta_from_file(filename):
    path = os.path.dirname(os.path.realpath(__file__)) + "/../rules/" + rchop(filename.replace(".yaml", ".meta"), ".disabled")
    return open(path)

def get_last_modification(modifications):
    last_modification = max(modifications, key=sorted)
    time, user = last_modification.items()[0]
    return {'user': user, 'datetime': time}

def get_last_modified_time(modifications):
    last_modification = get_last_modification(modifications)
    return last_modification['datetime']

def get_last_modified_by(modifications):
    last_modification = get_last_modification(modifications)
    return last_modification['user']

def rule_from_file(rule_file, filename):
    rule = yaml.safe_load(rule_file)
    meta = yaml.safe_load(meta_from_file(filename))
    if rule is not None and not 'error' in meta.keys():
        try:
            required_keys = ('name', 'filter', 'type', 'index', 'alert', 'email', 'es_host', 'es_port', 'smtp_host', 'email_reply_to')
            if all(keys in rule.keys() for keys in required_keys):
                return Rule(
                    name=rule['name'],
                    query=rule['filter'][0]['query']['query_string']['query'],
                    rule_type=rule['type'],
                    index=rule['index'],
                    alert=rule['alert'],
                    email=rule['email'],
                    es_host=rule['es_host'],
                    es_port=rule['es_port'],
                    smtp_host=rule['smtp_host'],
                    email_reply_to=rule['email_reply_to'],
                    author=meta['author'],
                    created=meta['created'],
                    modifications=meta['modifications'],
                    last_modified_time = get_last_modified_time(meta['modifications']),
                    last_modified_by = get_last_modified_by(meta['modifications']),
                    filename=filename
                )
            else:
                #need a ton of other metadata handling for these other instances
                try:
                    return Rule(
                        name=rule['name'],
                        filename=filename,
                        author=meta['author'],
                        created=meta['created'],
                        modifications=meta['modifications'],
                        last_modified_time = get_last_modified_time(
                            meta['modifications']
                        ),
                        last_modified_by = get_last_modified_by(
                            meta['modifications']
                        ),
                    )
                except:
                    return Rule(filename=filename)
        except:
            return Rule(filename=filename)
    return Rule(filename=filename)
