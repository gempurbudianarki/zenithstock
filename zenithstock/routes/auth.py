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
    if current_user.is_authenticated and not current_user.is_admin():
        return redirect(url_for('dashboard.index'))

    form = RegisterForm()
    in_app = current_user.is_authenticated and current_user.is_admin()

    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data

        if in_app:
            role = form.role.data
            status = 'active'
        else:
            role = 'staff'
            status = 'pending'

        new_user = User(username=username, role=role, status=status)
        new_user.set_password(password)

        try:
            db.session.add(new_user)
            db.session.commit()
            if in_app:
                flash(f'Akun pengguna "{username}" ({role.upper()}) berhasil dibuat!', 'success')
                return redirect(url_for('users.index'))
            flash('Registrasi berhasil! Akun Anda sedang ditinjau oleh Administrator.', 'success')
            return redirect(url_for('auth.login'))
        except Exception:
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
            if user.status != 'active':
                if user.status == 'pending':
                    flash('Akun Anda sedang ditinjau oleh Administrator. Harap tunggu persetujuan.', 'warning')
                else:
                    flash('Akun Anda telah dinonaktifkan. Hubungi Administrator.', 'danger')
                return redirect(url_for('auth.login'))

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


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form.get('old_password', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if not current_user.check_password(old_password):
            flash('Password lama salah.', 'danger')
        elif len(new_password) < 6:
            flash('Password baru minimal harus 6 karakter.', 'danger')
        elif new_password != confirm_password:
            flash('Konfirmasi password baru tidak cocok.', 'danger')
        else:
            current_user.set_password(new_password)
            db.session.commit()
            flash('Password Anda berhasil diperbarui!', 'success')
            return redirect(url_for('dashboard.index'))

    return render_template('auth/change_password.html')
