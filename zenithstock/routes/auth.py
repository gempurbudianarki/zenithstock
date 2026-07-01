from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from zenithstock import db
from zenithstock.models import User
from zenithstock.forms import RegisterForm, LoginForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def welcome():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return render_template('welcome.html')


@auth_bp.route('/filosofi-logo')
def filosofi_logo():
    return render_template('info/filosofi.html')


@auth_bp.route('/kebijakan-privasi')
def kebijakan_privasi():
    return render_template('info/privacy.html')


@auth_bp.route('/tentang-aplikasi')
def tentang_aplikasi():
    return render_template('info/about.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Only redirect if NOT admin – admin can access to add new users
    if current_user.is_authenticated and not current_user.is_admin():
        return redirect(url_for('dashboard.index'))
        
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data
        role = form.role.data
        
        # Create user
        new_user = User(username=username, role=role)
        new_user.set_password(password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash(f'Akun pengguna "{username}" ({role.upper()}) berhasil dibuat!', 'success')
            # Admin creating user → redirect to user management
            if current_user.is_authenticated and current_user.is_admin():
                return redirect(url_for('users.index'))
            flash('Registrasi berhasil! Silakan login untuk melanjutkan.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('Terjadi kesalahan saat menyimpan data. Silakan coba lagi.', 'danger')
            
    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
        
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            flash(f'Selamat datang kembali, {user.username} (Akses: {user.role.upper()})!', 'success')
            return redirect(next_page or url_for('dashboard.index'))
        else:
            flash('Username atau password salah.', 'danger')
            
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah berhasil logout.', 'info')
    return redirect(url_for('auth.welcome'))
