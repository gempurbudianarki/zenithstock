from flask import Blueprint, render_template, request
from flask_login import login_required
from zenithstock.models import StockMovement, Product, User
from zenithstock import db
from sqlalchemy import func
from datetime import datetime, timedelta

audit_bp = Blueprint('audit', __name__, url_prefix='/audit')


@audit_bp.route('/')
@login_required
def index():
    q = request.args.get('q', '').strip()
    tipe_f = request.args.get('type', '').strip()
    user_f = request.args.get('user_id', '').strip()
    date_from = request.args.get('date_from', '').strip()
    date_to = request.args.get('date_to', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 30

    query = StockMovement.query.join(Product)

    if q:
        query = query.filter(
            (Product.sku.ilike(f'%{q}%')) |
            (Product.nama_barang.ilike(f'%{q}%')) |
            (StockMovement.keterangan.ilike(f'%{q}%'))
        )
    if tipe_f:
        query = query.filter(StockMovement.tipe == tipe_f)

    if user_f:
        query = query.filter(StockMovement.user_id == int(user_f))

    if date_from:
        try:
            df = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(StockMovement.created_at >= df)
        except ValueError:
            pass

    if date_to:
        try:
            dt = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(StockMovement.created_at < dt)
        except ValueError:
            pass

    pagination = query.order_by(StockMovement.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    movements = pagination.items

    all_movements = StockMovement.query.all()
    total_masuk = sum(m.jumlah for m in all_movements if m.tipe == 'MASUK')
    total_keluar = sum(abs(m.jumlah) for m in all_movements if m.tipe == 'KELUAR')
    total_log = len(all_movements)

    users = User.query.order_by(User.username).all()

    if request.headers.get('HX-Request'):
        return render_template(
            'audit/_table.html',
            movements=movements,
            pagination=pagination,
            page=page,
            q=q,
            tipe_f=tipe_f,
            user_f=user_f,
            date_from=date_from,
            date_to=date_to
        )

    return render_template(
        'audit/index.html',
        movements=movements,
        pagination=pagination,
        total_masuk=total_masuk,
        total_keluar=total_keluar,
        total_log=total_log,
        users=users,
        page=page,
        q=q,
        tipe_f=tipe_f,
        user_f=user_f,
        date_from=date_from,
        date_to=date_to
    )
