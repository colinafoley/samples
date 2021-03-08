from gooclean import db
from orator.orm import belongs_to, has_many, belongs_to_many, has_many_through


class User(db.Model):
    __table__ = 'google.users'

    @has_many('owner', 'email')
    def files(self):
        return File

    @has_many('email','email')
    def xrefs(self):
        return Xref

    def __str__(self):
        return self.email + ' ' + self.accounts_last_login_time

class File(db.Model):
    __table__ = 'google.files'

    @belongs_to('email','owner')
    def user(self):
        return User

    def __str__(self):
        return self.title + ' ' + self.fileid

class Xref(db.Model):
    __table__ = 'google.xref'

    @belongs_to_many('email','email')
    def users(self):
        return User

    @belongs_to('fileid', 'fileid')
    def file(self):
        return File

    def __str__(self):
        return self.fileid + ' ' + self.email
