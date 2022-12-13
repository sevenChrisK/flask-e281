from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, DateTimeField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, InputRequired, Optional
from wtforms.fields import DateTimeLocalField
from app.models import User, Employee, Business, Shift



class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class NewEmployeeForm(FlaskForm):
    firstname = StringField('First name', validators=[DataRequired()])
    lastname = StringField('Last name', validators=[DataRequired()])
    hourly_rate = DecimalField('Hourly rate', places=2, validators=[DataRequired()])
    submit = SubmitField('Add employee')

    def validate_firstname(self, firstname):
        employee = Employee.query.filter_by(firstname=firstname.data, lastname=self.lastname.data).first()
        if employee is not None:
            raise ValidationError('Employee with same first and last name already exists.')

    def validate_lastname(self, lastname):
        employee = Employee.query.filter_by(firstname=self.firstname.data, lastname=lastname.data).first()
        if employee is not None:
            raise ValidationError('Employee with same first and last name already exists.')

    def validate_hourly_rate(self, hourly_rate):
        str_rate = str(hourly_rate.data)
        if "." not in str_rate:
            if int(str_rate) > 40:
                raise ValidationError('Hourly rate entered is too high!')
        else:
            if len(str_rate.split('.')[1]) > 2:
                print(str_rate.split('.')[1])
                raise ValidationError('Enter fewer decimal places, maximum of 2.')
            if len(str_rate.split('.')[0]) > 2:
                print(str_rate.split('.')[0])
                raise ValidationError('Triple figure hourly rate is too high!')


class NewBusinessForm(FlaskForm):
    name = StringField('Business name', validators=[DataRequired()])
    submit = SubmitField('Add business')

    def validate_name(self, name):
        business = Business.query.filter_by(name=name.data).first()
        if business is not None:
            raise ValidationError('Business with same name already exists.')


class NewShiftForm(FlaskForm):

    employee_id = SelectField(u'Employee', validators=[DataRequired()], id='employee')
    business_id = SelectField(u'Business', validators=[DataRequired()], id='business')
    start_time = DateTimeLocalField('Shift start', format='%Y-%m-%dT%H:%M', validators=[InputRequired()])
    finish_time = DateTimeLocalField('Shift finish', format='%Y-%m-%dT%H:%M', validators=[InputRequired()])
    submit = SubmitField('Add shift')

    def validate_start_time(self, start_time):
        if self.finish_time.data < start_time.data:
            raise ValidationError('Start time must be before finish time.')

    def validate_finish_time(self, finish_time):
        if finish_time.data < self.start_time.data:
            raise ValidationError('Finish time can not be before start time.')

    def validate_employee_id(self, employee_id):
        e = Employee.query.filter_by(id=employee_id.data).first()
        if e.wages is None:
            raise ValidationError(f'Employee does not have wages, add wages at http://127.0.0.1:5000/new_wage/{employee_id.data}')


class NewWageForm(FlaskForm):

    employee_id = SelectField(u'Employee', validators=[DataRequired()], id='employee')
    valid_from = DateTimeLocalField('Wage valid from', format='%Y-%m-%dT%H:%M', validators=[InputRequired()])
    valid_to = DateTimeLocalField('Wage valid to (optional)', format='%Y-%m-%dT%H:%M', validators=(Optional(),))
    is_current = BooleanField('This is the employee\'s current wage')
    hourly_rate = DecimalField('Hourly rate', places=2, validators=[DataRequired()])

    submit = SubmitField('Add wage')
