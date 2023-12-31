import secrets
import string
from flask import render_template, flash, redirect, url_for, request, current_app, session, jsonify, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db, mail, login
from app.forms import LoginForm, RegistrationForm, URegistrationForm, EntryForm, ExitForm, UpdateUser, UpdatePrice, PaymentForm
from app.models import User, ParkingSlot, ParkingPrice, ParkingHistory, Payment
from flask_principal import Permission, RoleNeed, Identity, AnonymousIdentity, identity_changed, identity_loaded
from datetime import datetime, timedelta
from time import time
import pytz
from random import randint

IST = pytz.timezone('Asia/Kolkata')

@login.unauthorized_handler
def unauthorized_callback():
    return redirect('/login?next=' + request.path)

@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    # Set the identity user object
    identity.user = current_user
    # Assuming the User model has a list of roles, update the
    # identity with the roles that the user provides
    if hasattr(current_user, 'role'):
        # for role in current_user.role:
        identity.provides.add(RoleNeed(str(current_user.role)))

admin_permission = Permission(RoleNeed('Admin'))
entry_permission = Permission(RoleNeed('Entry'))
exit_permission = Permission(RoleNeed('Exit'))
user_permission = Permission(RoleNeed('User'))
user_permission_all = entry_permission.union(exit_permission)
admin_entry_permission = admin_permission.union(entry_permission)
admin_exit_permission = admin_permission.union(exit_permission)
all_permission = admin_entry_permission.union(admin_exit_permission)


if not User.query.filter(User.email == 'example@gmail.com').first():
    user = User(username = 'ADMN001', email = 'example@gmail.com', name = 'Admin1', role = 'Admin')
    user.set_password('ADMN001')
    db.session.add(user)
    db.session.commit()

parking_price = ParkingPrice.query.order_by(ParkingPrice.id).first()
if parking_price is None:
    parking_price = ParkingPrice(date_updated = datetime.now(IST), charge = 50.0)
    db.session.add(parking_price)
    db.session.commit()

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
            return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        rol = ['Admin', 'Entry', 'Exit']
        user = User.query.filter_by(username=form.username.data, role='Admin'or 'Entry' or 'Exit').first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        identity_changed.send(current_app._get_current_object(), identity=Identity(user.id))
        next_page = request.args.get('next')
        if admin_permission or entry_permission or exit_permission or user_permission:
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/ulogin', methods=['GET', 'POST'])
def ulogin():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data, role='User').first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('ulogin'))
        login_user(user, remember=form.remember_me.data)
        identity_changed.send(current_app._get_current_object(), identity=Identity(user.id))
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('ulogin.html', title='Sign In', form=form)

@app.route('/uregister', methods=['GET', 'POST'])
def uregister():
    form = URegistrationForm()
    if form.validate_on_submit():
                user = User(username=form.username.data, name=form.name.data, email=form.email.data, role=form.role.data)
                password= form.password.data
                user.set_password(str(password))
                db.session.add(user)
                db.session.commit()
    return render_template('uregister.html', title='Register', form=form)



@app.route('/uentry', methods=['GET', 'POST'])
@login_required
def uentry():
    if user_permission:
        with user_permission.require(http_exception=403):
            form = EntryForm()
            if form.validate_on_submit():
                avail_space = ParkingSlot.query.order_by(ParkingSlot.id).all()
                count = 0
                for i in avail_space:
                    count+=1
                if count <= 100:
                    entry = ParkingSlot(rc = form.registration_no.data, phone = form.phone.data, name = form.name.data,
                                        entry_empname = current_user.name, entry_time = datetime.fromtimestamp(int(time()), IST), entry_epoch = int(time()))
                    db.session.add(entry)
                    db.session.commit()
                    flash(str(form.registration_no.data+' entered successfully!'))
                    return redirect('/uentry')
                else:
                    flash('No space available!')
                    return redirect('/uentry')
            return render_template('uentry.html', title='UserEntry', form=form)
    else:
        flash('Hmm, seems that you\'re not authorised to visit /entry!')
        return redirect(url_for('index'))


@app.route('/uexit', methods=['GET', 'POST'])
@login_required
def uexit():
    exitData = ParkingSlot.query.filter_by(entry_empname=current_user.name).all()
    return render_template('uexit.html', title = 'Exit', exitData=exitData)



@app.route('/logout')
@login_required
def logout():
    logout_user()
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)
    identity_changed.send(current_app._get_current_object(),identity=AnonymousIdentity())
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if admin_permission:
        with admin_permission.require(http_exception=403):
            form = RegistrationForm()
            if form.validate_on_submit():
                user = User(username=form.username.data,name=form.name.data, email=form.email.data, role=form.role.data)
                password = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for i in range(8))
                user.set_password(str(password))
                db.session.add(user)
                db.session.commit()
                text = str(form.username.data) + " = " + password
                with open("user_pass.txt", "a") as f:
                    f.write("\n"+text)
                return render_template('register-successful.html', title=str(form.username.data + ' registered successfully'), form=form, password=password)
            return render_template('register.html', title='Register', form=form)
    else:
        flash('Hmm, seems that you\'re not authorized to visit /register!')
        return redirect(url_for('index'))

@app.route('/entry', methods=['GET', 'POST'])
@login_required
def entry():
    if admin_entry_permission:
        with admin_entry_permission.require(http_exception=403):
            form = EntryForm()
            if form.validate_on_submit():
                avail_space = ParkingSlot.query.order_by(ParkingSlot.id).all()
                count = 0
                for i in avail_space:
                    count+=1
                if count <= 100:
                    entry = ParkingSlot(rc = form.registration_no.data, phone = form.phone.data, name = form.name.data,
                                        entry_empname = current_user.name, entry_time = datetime.fromtimestamp(int(time()), IST), entry_epoch = int(time()))
                    db.session.add(entry)
                    db.session.commit()
                    flash(str(form.registration_no.data+' entered successfully!'))
                    return redirect('/entry')
                else:
                    flash('No space available!')
                    return redirect('/entry')
            return render_template('entry.html', title='Entry', form=form)
    else:
        flash('Hmm, seems that you\'re not authorised to visit /entry!')
        return redirect(url_for('index'))

@app.route('/exit')
@login_required
def exit():
    if admin_exit_permission:
        with admin_exit_permission.require(http_exception=403):
            exitData = ParkingSlot.query.order_by(ParkingSlot.id).all()
            return render_template('exit.html', title = 'Exit', exitData=exitData)
    else:
        flash('Hmm, seems that you\'re not authorised to visit /exit!')
        return redirect(url_for('index'))

@app.route('/exit/<int:id>', methods=['GET','POST'])
@login_required
def exit_delete(id):
    if current_user.is_authenticated:
        if current_user.role=='Admin' or 'User' or 'Exit':
            get_car = ParkingSlot.query.get_or_404(id)
            form = ExitForm()
            ptime = int(time())-get_car.entry_epoch
            get_charge = ParkingPrice.query.order_by(ParkingPrice.date_updated).first()
            charge = get_charge.charge
            hour = get_hour(ptime)
            fare = charge * hour
            exit_time = int(time())
            time_stayed = str(timedelta(seconds=(exit_time-get_car.entry_epoch)))
            phone = str('******'+str(get_car.phone)[6:10])
            if form.validate_on_submit():
                upload_history = ParkingHistory(
                    rc = get_car.rc,
                    phone = get_car.phone,
                    name = get_car.name,
                    entry_empname= get_car.entry_empname,
                    entry_time = get_car.entry_time,
                    exit_time = datetime.fromtimestamp(exit_time, IST),
                    exit_empname = current_user.name,
                    time_stayed = time_stayed,
                    parking_charge = fare
                )
                upload_dues = Payment(
                    username = current_user.name,
                    charge = fare,
                    paid = 'NOT PAID'
                )
                db.session.add(upload_dues)
                db.session.add(upload_history)
                db.session.delete(get_car)
                db.session.commit()
                flash(str(get_car.rc + ' has been removed from your parking facility!'))
                if current_user.role == "User":
                    return redirect('/uexit')
                else:
                    return redirect('/exit')
            return render_template('exit-car.html', title = str(get_car.rc + ' - Exit'), car=get_car, form=form, fare=fare, phone=phone, time=time_stayed, exit_time=datetime.fromtimestamp(exit_time, IST))
    else:
        flash('Hmm, seems that you\'re not authorised to visit /exit!')
        return redirect(url_for('index'))

@app.route('/history')
@login_required
def history():
    if all_permission:
        with all_permission.require(http_exception=403):
            get_history = ParkingHistory.query.order_by(ParkingHistory.exit_time.desc()).all()
            return render_template('history.html', title = 'History', history = get_history)
    else:
        return 'You are on History page!'


@app.route('/manage-user')
@login_required
def manage():
    if admin_permission:
        with admin_permission.require(http_exception=403):
            all_user = User.query.order_by(User.id).all()
            return render_template('manage-user.html', title='Manage-User', all_user=all_user)
    else:
        flash('Hmm, trying to sneek into the manage user! You\'re not allowed!')
        return redirect(url_for('index'))

@app.route('/manage-user/update/<int:id>/<string:role>', methods = ['GET', 'POST'])
@login_required
def manage_update(id,role):
    if admin_permission:
        with admin_permission.require(http_exception=403):
            user = User.query.filter_by(id = id).first()
            form = UpdateUser()
            if form.validate_on_submit():
                user.email = form.email.data
                db.session.commit()
                flash('Data Successfully Updated!')
                return redirect('/manage-user')
            return render_template('update-user.html', form=form, user=user)
    else:
        flash('Hmm, trying to sneek into the manage user! You\'re not allowed!')
        return redirect(url_for('index'))


@app.route('/manage-user/delete/<int:id>/<string:role>')
@login_required
def manage_delete(id, role):
    if admin_permission:
        with admin_permission.require(http_exception=403):
            user = User.query.filter_by(id = id).first()
            if user.role != "Admin":
                db.session.delete(user)
                db.session.commit()
                flash('User Successfully Deleted!')
                return redirect('/manage-user')
            else:
                flash('Error!')
                return redirect('/manage-user')
    else:
        flash('Hmm, trying to sneek into the manage user! You\'re not allowed!')
        return redirect(url_for('index'))

@app.route('/manage-parking', methods = ['GET', 'POST'])
@login_required
def manage_parking():
    timestp = int(time())
    if admin_permission:
        with admin_permission.require(http_exception=403):
            parkinghistory = ParkingHistory.query.order_by(ParkingHistory.id).all()
            income = 0
            for data in parkinghistory:
                income = income + data.parking_charge
            parking_price = ParkingPrice.query.order_by(ParkingPrice.date_updated).first()
            date_updated = parking_price.date_updated
            charge = parking_price.charge
            form = UpdatePrice()
            if form.validate_on_submit():
                parking_price.charge = form.charge.data
                parking_price.date_updated = datetime.fromtimestamp(timestp, IST)
                db.session.commit()
                flash('Charges Successfully Updated!')
                return redirect('/manage-parking')
            return render_template('manage-parking.html', form=form, title='Manage Parking', income=income, date=date_updated, charge = charge)
    else:
        flash('Hmm, trying to sneek into the manage parking facility page! You\'re not allowed!')
        return redirect(url_for('index'))

@app.route('/available-space')
@admin_entry_permission.require(http_exception=403)
def available_space():
    avail_space = ParkingSlot.query.order_by(ParkingSlot.id).all()
    count = 0
    for i in avail_space:
        count+=1
    return str(100-count)

@app.route('/dues', methods=['GET', 'POST'])
@login_required
def dues():  
            dueData = Payment.query.filter_by(username=current_user.name).all()
            return render_template('dues.html',title='Dues',dueData=dueData)

@app.route('/transactions', methods=['GET', 'POST'])
@login_required
def transactions():  
            payData = Payment.query.order_by(Payment.id).all()
            return render_template('transactions.html',title='Transactions',payData=payData)

@app.route('/payment/<int:id>', methods=['GET','POST'])
@login_required
def payment(id):
    form = PaymentForm()
    if form.validate_on_submit():
        pid = randint(1000000,9999999)
        payment = Payment.query.filter_by(id=id).first()
        payment.paymentType = form.type.data
        payment.paid = "PAID"
        payment.paymentDate = datetime.fromtimestamp(int(time()), IST)
        payment.paymentID = pid
        db.session.commit()
        flash('Payment Successful!!')
        return redirect('/index')
    return render_template('payment.html', title='Payment',form=form)

@app.route('/about')
def about():
    return 'Currently working on it!'

def get_hour(seconds):
    hour = seconds//3600
    seconds %= 3600
    minute = seconds // 60
    seconds %= 60

    if hour == 0:
        hour += 1
    else:
        if minute < 60 and minute > 0:
            hour+=1
        else:
            if seconds < 60 and seconds > 0:
                minute +=1
                if minute < 60 and minute > 0:
                    hour+=1
    return hour

@app.route('/get-ip-address')
def get_ip():
    return jsonify({'ip': request.headers['X-Real-IP']}), 200

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', title='Page Not Found!'),404

@app.errorhandler(403)
def unauthorised_error(e):
    return render_template('403.html', title='Unauthorised'),403

@app.route('/view-files')
def templates():
    return render_template('view-templates.html')

@app.route('/view/<variable>')
def returntemp(variable):
    return send_from_directory('templates', variable, mimetype='text/plain')