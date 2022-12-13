from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime, timedelta

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    roles = db.relationship('Role', secondary='user_roles')

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)


class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Business(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True, unique=True, nullable=False)
    shifts = db.relationship('Shift', backref='business', lazy=True)

    def __repr__(self):
        return f'<Business {self.name}>'


class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(64), index=True, nullable=False)
    lastname = db.Column(db.String(64), index=True, nullable=False)
    wages = db.relationship('Wage', backref='employee', lazy=False)
    shifts = db.relationship('Shift', backref='employee', lazy=True)
    fullname = db.column_property(firstname + " " + lastname)

    def __repr__(self):
        return f'<Employee {self.firstname} {self.lastname}>'


class Shift(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    business_id = db.Column(db.Integer, db.ForeignKey('business.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    finish_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<Shift {self.id}>'

    @hybrid_property
    def shift_length(self):
        td: timedelta = self.finish_time - self.start_time
        length_in_hours = td.total_seconds() / 3600
        return length_in_hours

    @hybrid_property
    def shift_cost(self):
        e = Employee.query.filter_by(id=self.employee_id).first()
        wage = 10.42
        for w in e.wages:
            if w.valid_from < self.start_time and (w.is_current or (w.valid_to is not None and w.valid_to > self.finish_time)):
                wage = w.hourly_rate
            else:
                wage = 10.42

        return self.shift_length * wage


class Wage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    hourly_rate = db.Column(db.Float, nullable=False)
    valid_from = db.Column(db.DateTime, nullable=False)
    valid_to = db.Column(db.DateTime, nullable=True)
    is_current = db.Column(db.Boolean, nullable=False)
