from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from zenithstock import db
from zenithstock.models import Supplier, Product
from zenithstock.forms import SupplierForm

suppliers_bp = Blueprint('suppliers', __name__, url_prefix='/suppliers')


@suppliers_bp.route('/')
@login_required
def index():
    search_query = request.args.get('q', '').strip()

    query = Supplier.query
    if search_query:
        query = query.filter(
            (Supplier.nama.ilike(f'%{search_query}%')) |
            (Supplier.kontak.ilike(f'%{search_query}%')) |
            (Supplier.alamat.ilike(f'%{search_query}%'))
        )

    suppliers = query.order_by(Supplier.nama).all()
    products_with_supplier = Product.query.filter(Product.supplier_id.isnot(None)).count()

    if request.headers.get('HX-Request'):
        return render_template('suppliers/_table.html', suppliers=suppliers, search_query=search_query)

    return render_template(
        'suppliers/index.html',
        suppliers=suppliers,
        search_query=search_query,
        products_with_supplier=products_with_supplier
    )


@suppliers_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = SupplierForm()
    if form.validate_on_submit():
        nama = form.nama.data.strip()
        kontak = form.kontak.data.strip()
        telepon = form.telepon.data.strip()
        alamat = form.alamat.data.strip()

        new_supplier = Supplier(nama=nama, kontak=kontak, telepon=telepon, alamat=alamat)

        try:
            db.session.add(new_supplier)
            db.session.commit()
            flash(f'Supplier "{nama}" berhasil ditambahkan!', 'success')
            return redirect(url_for('suppliers.index'))
        except Exception:
            db.session.rollback()
            flash('Gagal menambahkan supplier. Silakan coba lagi.', 'danger')

    return render_template('suppliers/create.html', form=form)


@suppliers_bp.route('/edit/<int:supplier_id>', methods=['GET', 'POST'])
@login_required
def edit(supplier_id):
    supplier = Supplier.query.get_or_404(supplier_id)
    form = SupplierForm(obj=supplier, supplier_id=supplier_id)

    if form.validate_on_submit():
        supplier.nama = form.nama.data.strip()
        supplier.kontak = form.kontak.data.strip()
        supplier.telepon = form.telepon.data.strip()
        supplier.alamat = form.alamat.data.strip()

        try:
            db.session.commit()
            flash(f'Data supplier "{supplier.nama}" berhasil diperbarui!', 'success')
            return redirect(url_for('suppliers.index'))
        except Exception:
            db.session.rollback()
            flash('Gagal memperbarui data supplier. Silakan coba lagi.', 'danger')

    return render_template('suppliers/edit.html', form=form, supplier=supplier)


@suppliers_bp.route('/delete/<int:supplier_id>', methods=['POST'])
@login_required
def delete(supplier_id):
    if not current_user.is_admin():
        flash('Otorisasi gagal! Hanya Administrator yang berwenang menghapus data supplier.', 'danger')
        return redirect(url_for('suppliers.index'))

    supplier = Supplier.query.get_or_404(supplier_id)
    nama = supplier.nama

    try:
        db.session.delete(supplier)
        db.session.commit()
        flash(f'Supplier "{nama}" berhasil dihapus.', 'success')
    except Exception:
        db.session.rollback()
        flash(
            f'Gagal menghapus supplier "{nama}". '
            f'Kemungkinan supplier ini sedang digunakan oleh data barang.',
            'danger'
        )

    if request.headers.get('HX-Request'):
        search_query = request.args.get('q', '').strip()
        query = Supplier.query
        if search_query:
            query = query.filter(Supplier.nama.ilike(f'%{search_query}%'))
        suppliers = query.order_by(Supplier.nama).all()
        return render_template('suppliers/_table.html', suppliers=suppliers)

    return redirect(url_for('suppliers.index'))
