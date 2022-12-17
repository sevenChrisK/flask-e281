from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime

from app import app, db
from app.forms import LoginForm, RegistrationForm, NewEmployeeForm, NewBusinessForm, NewShiftForm, NewWageForm, NewUserRoleForm
from app.models import User, Employee, Business, Shift, Wage, Role, UserRoles

@app.context_processor
def inject_businesses_list():
    return dict(businesses_list=Business.query.all())

def role_check(required_role: str = 'Admin'):
    current_user_roles = [r.name for r in current_user.roles]
    if required_role == 'Admin' and 'Admin' not in current_user_roles:
        abort(401)
    if required_role not in current_user_roles and 'Admin' not in current_user_roles:
        abort(401)

@app.route('/')
@app.route('/index')
@login_required
def index():

    return render_template('index.html', title='Home')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/new_employee', methods=['GET', 'POST'])
@login_required
def new_employee():
    role_check('Manager')

    form = NewEmployeeForm()
    if form.validate_on_submit():

        employee = Employee(firstname=form.firstname.data, lastname=form.lastname.data)
        db.session.add(employee)
        db.session.commit()

        wage = Wage(employee_id=employee.id, hourly_rate=form.hourly_rate.data, valid_from=datetime.now(),
                    is_current=True)
        db.session.add(wage)

        db.session.commit()

        flash(f'New employee, {employee.firstname} {employee.lastname}, successfully added!')
        return redirect(url_for('new_employee'))
    return render_template('new_employee.html', title='New employee', form=form)


@app.route('/new_business', methods=['GET', 'POST'])
@login_required
def new_business():
    role_check("Manager")
    form = NewBusinessForm()
    if form.validate_on_submit():
        business = Business(name=form.name.data)
        db.session.add(business)
        db.session.commit()
        flash(f'New business, {business.name}, successfully added!')
        return redirect(url_for('new_business'))
    return render_template('new_business.html', title='New business', form=form)


@app.route('/new_shift', methods=['GET', 'POST'])
@login_required
def new_shift():
    role_check("Manager")
    form = NewShiftForm()
    form.employee_id.choices = [(e.id, f'{e.firstname} {e.lastname}') for e in Employee.query.order_by('firstname')]
    form.business_id.choices = [(b.id, b.name) for b in Business.query.order_by('name')]
    if form.validate_on_submit():
        shift = Shift(start_time=form.start_time.data,
                      finish_time=form.finish_time.data,
                      employee_id=form.employee_id.data,
                      business_id=form.business_id.data)
        db.session.add(shift)
        db.session.commit()
        flash(f'New shift successfully added!')
        return redirect(url_for('new_shift'))
    return render_template('new_shift.html', title='New shift', form=form)


@app.route('/new_wage/<int:employee_id>', methods=['GET', 'POST'])
@login_required
def new_wage(employee_id):
    role_check('Manager')
    form = NewWageForm()
    e = Employee.query.filter_by(id=employee_id).first()
    form.employee_id.choices = [(e.id, f'{e.firstname} {e.lastname}')]
    if form.validate_on_submit():
        check_for_existing_wage = Wage.query.filter_by(employee_id=employee_id, is_current=True).first()
        has_existing_wage = True if check_for_existing_wage is not None else False
        if form.is_current.data and has_existing_wage:
            check_for_existing_wage.is_current = False
            db.session.commit()
        wage = Wage(employee_id=form.employee_id.data,
                      valid_from=form.valid_from.data,
                      valid_to=form.valid_to.data,
                      hourly_rate=form.hourly_rate.data,
                      is_current=form.is_current.data)
        db.session.add(wage)
        db.session.commit()
        flash(f'Wage successfully updated!')
        return redirect(url_for('new_wage', employee_id=employee_id))
    return render_template('new_wage.html', title='New wage', form=form)


@app.route('/list_shifts', methods=['GET', 'POST'])
@login_required
def list_shifts():
    shifts = Shift.query.all()

    return render_template('shifts.html', title='Shifts list', shifts=shifts)


@app.route('/shift/<int:shift_id>', methods=['GET', 'POST'])
@login_required
def shift(shift_id):
    shift = Shift.query.filter_by(id=shift_id).first()

    return render_template('shifts.html', title='Shifts list', shifts=[shift])


@app.route('/employee/<int:employee_id>', methods=['GET', 'POST'])
@login_required
def employee(employee_id):
    shifts = Shift.query.filter_by(employee_id=employee_id)

    return render_template('shifts.html', title='Shifts list', shifts=shifts)


@app.route('/business/<int:business_id>', methods=['GET', 'POST'])
@login_required
def business(business_id):
    shifts = Shift.query.filter_by(business_id=business_id)

    return render_template('shifts.html', title='Shifts list', shifts=shifts)


@app.route('/new_user_roles', methods=['GET', 'POST'])
@login_required
def new_user_roles():
    role_check()
    form = NewUserRoleForm()
    form.user_id.choices = [(u.id, u.usernamename) for u in User.query.order_by('username')]
    form.role_id.choices = [(r.id, r.name) for r in Role.query.all()]

    if form.validate_on_submit():
        user_role = UserRoles(user_id=form.user_id.data,
                      role_id=form.role_id.data)
        db.session.add(user_role)
        db.session.commit()
        flash(f'New user role successfully added!')
        return redirect(url_for('new_user_roles'))
    
    return render_template('new_user_role.html', title='New user role', form=form)


