from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from zenithstock import db
from zenithstock.models import Product, StockMovement
from zenithstock.forms import StockMovementForm

movements_bp = Blueprint('movements', __name__, url_prefix='/movements')


@movements_bp.route('/')
@login_required
def index():
    search_query = request.args.get('q', '').strip()
    type_filter = request.args.get('type', '').strip()

    query = StockMovement.query.join(Product)

    if search_query:
        query = query.filter(
            (Product.sku.ilike(f'%{search_query}%')) |
            (Product.nama_barang.ilike(f'%{search_query}%')) |
            (StockMovement.keterangan.ilike(f'%{search_query}%'))
        )

    if type_filter:
        query = query.filter(StockMovement.tipe == type_filter)

    movements = query.order_by(StockMovement.created_at.desc()).all()

    total_log = len(movements)
    total_masuk = sum(1 for m in movements if m.tipe == 'MASUK')
    total_keluar = sum(1 for m in movements if m.tipe == 'KELUAR')

    if request.headers.get('HX-Request'):
        return render_template('movements/_table.html', movements=movements)

    return render_template(
        'movements/index.html',
        movements=movements,
        search_query=search_query,
        type_filter=type_filter,
        total_log=total_log,
        total_masuk=total_masuk,
        total_keluar=total_keluar
    )


@movements_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = StockMovementForm()

    product_id_param = request.args.get('product_id', type=int)
    if request.method == 'GET' and product_id_param:
        product = Product.query.get(product_id_param)
        if product:
            form.product_id.data = product.id

    if form.validate_on_submit():
        product_id = form.product_id.data
        tipe = form.tipe.data
        jumlah = form.jumlah.data
        keterangan = form.keterangan.data.strip()

        product = Product.query.get_or_404(product_id)

        qty_change = 0
        if tipe == 'MASUK':
            qty_change = jumlah
        elif tipe == 'KELUAR':
            qty_change = -jumlah
            if product.stok < jumlah:
                flash(
                    f'Transaksi ditolak! Stok "{product.nama_barang}" saat ini ({product.stok} unit) '
                    f'tidak mencukupi untuk pengeluaran sebanyak {jumlah} unit.',
                    'danger'
                )
                return render_template('movements/create.html', form=form)
        elif tipe == 'PENYESUAIAN':
            qty_change = jumlah

        product.stok += qty_change

        movement = StockMovement(
            product_id=product.id,
            user_id=current_user.id,
            jumlah=qty_change,
            tipe=tipe,
            keterangan=keterangan or f"Mutasi {tipe} oleh {current_user.username}"
        )

        try:
            db.session.add(movement)
            db.session.commit()
            flash(
                f'Transaksi mutasi stok berhasil dicatat! '
                f'Stok "{product.nama_barang}" diperbarui menjadi {product.stok} unit.',
                'success'
            )
            return redirect(url_for('movements.index'))
        except Exception:
            db.session.rollback()
            flash('Gagal mencatat transaksi mutasi stok. Silakan coba lagi.', 'danger')

    return render_template('movements/create.html', form=form)
