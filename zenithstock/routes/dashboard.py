from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from zenithstock import db
from zenithstock.models import Product, StockMovement
from zenithstock.forms import ProductForm

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard_bp.route('/')
@login_required
def index():
    search_query = request.args.get('q', '').strip()
    category_filter = request.args.get('category', '').strip()
    status_filter = request.args.get('filter', '').strip()

    query = Product.query.filter(Product.is_deleted == False)

    if search_query:
        query = query.filter(
            (Product.nama_barang.ilike(f'%{search_query}%')) |
            (Product.sku.ilike(f'%{search_query}%')) |
            (Product.kategori.ilike(f'%{search_query}%'))
        )
    if category_filter:
        query = query.filter(Product.kategori == category_filter)

    if status_filter == 'critical':
        query = query.filter(Product.stok > 0, Product.stok <= Product.min_stok)
    elif status_filter == 'empty':
        query = query.filter(Product.stok == 0)

    products = query.order_by(Product.sku).all()

    if request.headers.get('HX-Request'):
        return render_template('dashboard/_table.html', products=products)

    all_products = Product.query.filter(Product.is_deleted == False).all()
    total_products = len(all_products)
    total_stock = sum(p.stok for p in all_products)
    out_of_stock_count = sum(1 for p in all_products if p.stok == 0)
    low_stock_count = sum(1 for p in all_products if 0 < p.stok <= p.min_stok)
    total_valuation = sum(p.stok * p.harga for p in all_products)

    categories = db.session.query(Product.kategori).filter(Product.is_deleted == False).distinct().all()
    categories = [c[0] for c in categories if c[0]]

    return render_template(
        'dashboard/index.html',
        products=products,
        total_products=total_products,
        total_stock=total_stock,
        out_of_stock_count=out_of_stock_count,
        low_stock_count=low_stock_count,
        total_valuation=total_valuation,
        categories=categories,
        search_query=search_query,
        category_filter=category_filter
    )


@dashboard_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = ProductForm()
    if form.validate_on_submit():
        sku = form.sku.data.strip().upper()
        nama = form.nama_barang.data.strip()
        kategori = form.kategori.data.strip()
        stok = form.stok.data
        harga = form.harga.data
        min_stok = form.min_stok.data
        lokasi_rak = form.lokasi_rak.data.strip()

        supplier_id = form.supplier_id.data
        if supplier_id == -1:
            supplier_id = None

        new_product = Product(
            sku=sku,
            nama_barang=nama,
            kategori=kategori,
            stok=stok,
            harga=harga,
            min_stok=min_stok,
            lokasi_rak=lokasi_rak or None,
            supplier_id=supplier_id
        )

        try:
            db.session.add(new_product)
            db.session.commit()

            if stok > 0:
                initial_movement = StockMovement(
                    product_id=new_product.id,
                    user_id=current_user.id,
                    jumlah=stok,
                    tipe='MASUK',
                    keterangan='Stok awal barang baru'
                )
                db.session.add(initial_movement)
                db.session.commit()

            flash(f'Barang dengan SKU {sku} berhasil ditambahkan!', 'success')
            return redirect(url_for('dashboard.index'))
        except Exception:
            db.session.rollback()
            flash('Gagal menyimpan data barang. Silakan coba lagi.', 'danger')

    return render_template('dashboard/create.html', form=form)


@dashboard_bp.route('/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit(product_id):
    product = Product.query.get_or_404(product_id)
    if product.is_deleted:
        abort(404)
    form = ProductForm(obj=product, product_id=product_id)

    if form.validate_on_submit():
        product.sku = form.sku.data.strip().upper()
        product.nama_barang = form.nama_barang.data.strip()
        product.kategori = form.kategori.data.strip()
        if current_user.is_admin():
            product.harga = form.harga.data
        product.min_stok = form.min_stok.data
        product.lokasi_rak = form.lokasi_rak.data.strip() or None

        supplier_id = form.supplier_id.data
        product.supplier_id = None if supplier_id == -1 else supplier_id

        old_stok = product.stok
        new_stok = form.stok.data

        if old_stok != new_stok:
            diff = new_stok - old_stok
            product.stok = new_stok
            adjustment_movement = StockMovement(
                product_id=product.id,
                user_id=current_user.id,
                jumlah=diff,
                tipe='PENYESUAIAN',
                keterangan=f'Penyesuaian stok manual dari {old_stok} ke {new_stok}'
            )
            db.session.add(adjustment_movement)

        try:
            db.session.commit()
            flash(f'Data barang SKU {product.sku} berhasil diperbarui!', 'success')
            return redirect(url_for('dashboard.index'))
        except Exception:
            db.session.rollback()
            flash('Gagal memperbarui data barang. Silakan coba lagi.', 'danger')

    if request.method == 'GET':
        form.supplier_id.data = product.supplier_id if product.supplier_id else -1
        form.stok.data = product.stok

    return render_template('dashboard/edit.html', form=form, product=product)


@dashboard_bp.route('/delete/<int:product_id>', methods=['POST', 'DELETE'])
@login_required
def delete(product_id):
    if not current_user.is_admin():
        flash('Otorisasi gagal! Hanya Administrator yang berwenang menghapus data barang.', 'danger')
        return abort(403)

    product = Product.query.get_or_404(product_id)
    if product.is_deleted:
        abort(404)
    sku = product.sku
    try:
        product.is_deleted = True
        db.session.commit()
        flash(f'Barang SKU {sku} berhasil dihapus.', 'success')
    except Exception:
        db.session.rollback()
        flash(f'Gagal menghapus barang SKU {sku}.', 'danger')

    if request.headers.get('HX-Request'):
        search_query = request.form.get('q', request.args.get('q', '')).strip()
        category_filter = request.form.get('category', request.args.get('category', '')).strip()

        query = Product.query.filter(Product.is_deleted == False)
        if search_query:
            query = query.filter(
                (Product.nama_barang.ilike(f'%{search_query}%')) |
                (Product.sku.ilike(f'%{search_query}%')) |
                (Product.kategori.ilike(f'%{search_query}%'))
            )
        if category_filter:
            query = query.filter(Product.kategori == category_filter)

        products = query.order_by(Product.sku).all()
        return render_template(
            'dashboard/_table.html',
            products=products,
            search_query=search_query,
            category_filter=category_filter
        )

    return redirect(url_for('dashboard.index'))
