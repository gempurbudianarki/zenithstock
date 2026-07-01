from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from zenithstock.models import Product, StockMovement, Supplier
from zenithstock import db
from sqlalchemy import func
from datetime import datetime, timedelta

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')


@analytics_bp.route('/')
@login_required
def index():
    all_products = Product.query.all()

    total_products = len(all_products)
    total_stock = sum(p.stok for p in all_products)
    total_valuation = sum(p.stok * p.harga for p in all_products)
    low_stock_count = sum(1 for p in all_products if 0 < p.stok <= p.min_stok)
    out_of_stock = sum(1 for p in all_products if p.stok == 0)
    total_suppliers = Supplier.query.count()

    cat_data = (
        db.session.query(Product.kategori, func.count(Product.id), func.sum(Product.stok * Product.harga))
        .group_by(Product.kategori)
        .all()
    )
    categories = [r[0] for r in cat_data]
    cat_product_cnt = [r[1] for r in cat_data]
    cat_valuation = [int(r[2] or 0) for r in cat_data]

    top_products = sorted(all_products, key=lambda p: p.stok * p.harga, reverse=True)[:10]

    normal_count = sum(1 for p in all_products if p.stok > p.min_stok)
    critical_count = low_stock_count
    empty_count = out_of_stock

    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    movements_30d = StockMovement.query.filter(StockMovement.created_at >= thirty_days_ago).all()

    trend_labels = []
    trend_masuk = []
    trend_keluar = []
    for i in range(13, -1, -1):
        day = datetime.utcnow() - timedelta(days=i)
        label = day.strftime('%d/%m')
        trend_labels.append(label)

        masuk = sum(
            m.jumlah for m in movements_30d
            if m.created_at.date() == day.date() and m.tipe == 'MASUK'
        )
        keluar = sum(
            abs(m.jumlah) for m in movements_30d
            if m.created_at.date() == day.date() and m.tipe == 'KELUAR'
        )
        trend_masuk.append(masuk)
        trend_keluar.append(keluar)

    total_masuk = StockMovement.query.filter_by(tipe='MASUK').count()
    total_keluar = StockMovement.query.filter_by(tipe='KELUAR').count()
    total_sesuai = StockMovement.query.filter_by(tipe='PENYESUAIAN').count()

    critical_products = [p for p in all_products if 0 < p.stok <= p.min_stok]
    critical_products.sort(key=lambda p: p.stok)

    return render_template(
        'analytics/index.html',
        total_products=total_products,
        total_stock=total_stock,
        total_valuation=total_valuation,
        low_stock_count=low_stock_count,
        out_of_stock=out_of_stock,
        total_suppliers=total_suppliers,
        categories=categories,
        cat_product_cnt=cat_product_cnt,
        cat_valuation=cat_valuation,
        top_products=top_products,
        normal_count=normal_count,
        critical_count=critical_count,
        empty_count=empty_count,
        trend_labels=trend_labels,
        trend_masuk=trend_masuk,
        trend_keluar=trend_keluar,
        total_masuk=total_masuk,
        total_keluar=total_keluar,
        total_sesuai=total_sesuai,
        critical_products=critical_products,
    )


@analytics_bp.route('/api/chart-data')
@login_required
def chart_data():
    all_products = Product.query.all()
    total_val = sum(p.stok * p.harga for p in all_products)
    return jsonify({"total_valuation": total_val, "total_products": len(all_products)})
