from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from zenithstock import db
from zenithstock.models import User, StockMovement

users_bp = Blueprint('users', __name__, url_prefix='/users')


def admin_required(f):
    """Decorator – hanya admin yang boleh akses"""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated


@users_bp.route('/')
@login_required
@admin_required
def index():
    """Daftar semua pengguna sistem"""
    q = request.args.get('q', '').strip()
    role_filter = request.args.get('role', '').strip()

    query = User.query
    if q:
        query = query.filter(User.username.ilike(f'%{q}%'))
    if role_filter:
        query = query.filter(User.role == role_filter)

    users = query.order_by(User.username).all()

    # Attach movement count per user
    user_stats = {}
    for u in users:
        cnt = StockMovement.query.filter_by(user_id=u.id).count()
        user_stats[u.id] = cnt

    # HTMX partial
    if request.headers.get('HX-Request'):
        return render_template('users/_table.html',
                               users=users, user_stats=user_stats, q=q, role_filter=role_filter)

    return render_template('users/index.html',
                           users=users, user_stats=user_stats,
                           q=q, role_filter=role_filter,
                           total_users=User.query.count(),
                           total_admin=User.query.filter_by(role='admin').count(),
                           total_staff=User.query.filter_by(role='staff').count())


@users_bp.route('/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(user_id):
    """Ubah data user – role, reset password"""
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        action = request.form.get('action')

        # ── Change Role ───────────────────────────────────
        if action == 'change_role':
            new_role = request.form.get('role')
            if new_role not in ('admin', 'staff'):
                flash('Peran tidak valid.', 'danger')
            elif user.id == current_user.id and new_role != 'admin':
                flash('Anda tidak dapat menurunkan peran akun Anda sendiri.', 'warning')
            else:
                user.role = new_role
                db.session.commit()
                flash(f'Peran pengguna "{user.username}" diubah menjadi {new_role.upper()}.', 'success')
            return redirect(url_for('users.index'))

        # ── Reset Password ────────────────────────────────
        elif action == 'reset_password':
            new_pw  = request.form.get('new_password', '').strip()
            confirm = request.form.get('confirm_password', '').strip()
            if len(new_pw) < 6:
                flash('Password baru minimal 6 karakter.', 'danger')
            elif new_pw != confirm:
                flash('Konfirmasi password tidak cocok.', 'danger')
            else:
                user.set_password(new_pw)
                db.session.commit()
                flash(f'Password pengguna "{user.username}" berhasil direset.', 'success')
            return redirect(url_for('users.index'))

    # Movement count for this user
    movement_count = StockMovement.query.filter_by(user_id=user.id).count()
    return render_template('users/edit.html', user=user, movement_count=movement_count)


@users_bp.route('/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete(user_id):
    """Hapus user – tidak bisa hapus diri sendiri"""
    if user_id == current_user.id:
        flash('Anda tidak dapat menghapus akun Anda sendiri yang sedang aktif.', 'danger')
        return redirect(url_for('users.index'))

    user = User.query.get_or_404(user_id)
    username = user.username

    # Cek apakah user punya movement log – jika ada, beri peringatan
    movement_count = StockMovement.query.filter_by(user_id=user_id).count()
    if movement_count > 0:
        flash(f'Pengguna "{username}" memiliki {movement_count} log transaksi. '
              f'Data log tetap tersimpan namun referensi pengguna akan terputus.', 'warning')

    try:
        # Set user_id in movements to NULL (orphan) sebelum hapus user
        StockMovement.query.filter_by(user_id=user_id).update({'user_id': current_user.id})
        db.session.delete(user)
        db.session.commit()
        flash(f'Pengguna "{username}" berhasil dihapus dari sistem.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Gagal menghapus pengguna "{username}". Error: {str(e)}', 'danger')

    if request.headers.get('HX-Request'):
        users = User.query.order_by(User.username).all()
        user_stats = {u.id: StockMovement.query.filter_by(user_id=u.id).count() for u in users}
        return render_template('users/_table.html', users=users, user_stats=user_stats, q='', role_filter='')

    return redirect(url_for('users.index'))


@users_bp.route('/toggle-role/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def toggle_role(user_id):
    """Toggle role admin/staff dengan HTMX"""
    if user_id == current_user.id:
        flash('Anda tidak dapat mengubah peran akun sendiri.', 'warning')
        return redirect(url_for('users.index'))

    user = User.query.get_or_404(user_id)
    user.role = 'staff' if user.role == 'admin' else 'admin'
    db.session.commit()
    flash(f'Peran "{user.username}" diubah ke {user.role.upper()}.', 'success')
    return redirect(url_for('users.index'))
