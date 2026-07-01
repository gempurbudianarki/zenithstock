from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from zenithstock import db
from zenithstock.models import Product, StockMovement
from zenithstock.forms import StockMovementForm

movements_bp = Blueprint('movements', __name__, url_prefix='/movements')

@movements_bp.route('/')
@login_required
def index():
    # Read search filters
    search_query = request.args.get('q', '').strip()
    type_filter = request.args.get('type', '').strip()
    
    # Query with join to product to support searching by product name or SKU
    query = StockMovement.query.join(Product)
    
    if search_query:
        query = query.filter(
            (Product.sku.ilike(f'%{search_query}%')) |
            (Product.nama_barang.ilike(f'%{search_query}%')) |
            (StockMovement.keterangan.ilike(f'%{search_query}%'))
        )
        
    if type_filter:
        query = query.filter(StockMovement.tipe == type_filter)
        
    movements   = query.order_by(StockMovement.created_at.desc()).all()
    
    # Compute stats in Python (Jinja2 doesn't support selectattr 'eq' natively)
    total_log    = len(movements)
    total_masuk  = sum(1 for m in movements if m.tipe == 'MASUK')
    total_keluar = sum(1 for m in movements if m.tipe == 'KELUAR')
    
    # If HTMX, return the partial log table
    if request.headers.get('HX-Request'):
        return render_template('movements/_table.html', movements=movements)
        
    return render_template('movements/index.html', movements=movements,
                           search_query=search_query, type_filter=type_filter,
                           total_log=total_log, total_masuk=total_masuk, total_keluar=total_keluar)


@movements_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = StockMovementForm()
    
    # Pre-select product if passed in GET params
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
        
        # Calculate stock change
        qty_change = 0
        if tipe == 'MASUK':
            qty_change = jumlah
        elif tipe == 'KELUAR':
            qty_change = -jumlah
            # Validate if stock is sufficient
            if product.stok < jumlah:
                flash(f'Transaksi ditolak! Stok "{product.nama_barang}" saat ini ({product.stok} unit) tidak mencukupi untuk pengeluaran sebanyak {jumlah} unit.', 'danger')
                return render_template('movements/create.html', form=form)
        elif tipe == 'PENYESUAIAN':
            # For adjustments, let the user specify quantity change directly (can be positive or negative)
            # To make it user-friendly, let's treat the form field 'jumlah' as positive, 
            # and determine sign based on a dropdown or context. 
            # In our form, if user inputs 5, it means we adjust by +5 or -5. Let's check how the user wants it.
            # To make it simple: let's ask them to write the target stock or positive/negative change.
            # Let's say in PENYESUAIAN, we interpret the number as a positive or negative adjustment 
            # based on user input. We can accept signed integer. But standard wtforms IntegerField handles negative values too.
            # If they enter positive it increases, negative decreases.
            qty_change = jumlah # can be negative if entered so, or we default to positive.
            
        # Update product stock
        product.stok += qty_change
        
        # Create movement log
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
            flash(f'Transaksi mutasi stok berhasil dicatat! Stok "{product.nama_barang}" diperbarui menjadi {product.stok} unit.', 'success')
            return redirect(url_for('movements.index'))
        except Exception as e:
            db.session.rollback()
            flash('Gagal mencatat transaksi mutasi stok. Silakan coba lagi.', 'danger')
            
    return render_template('movements/create.html', form=form)
