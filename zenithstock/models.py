from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from zenithstock import db


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='staff')
    status = db.Column(db.String(20), nullable=False, default='pending')

    @property
    def is_active(self):
        return self.status == 'active'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


class Supplier(db.Model):
    __tablename__ = 'suppliers'

    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), unique=True, nullable=False, index=True)
    kontak = db.Column(db.String(100))
    telepon = db.Column(db.String(30))
    alamat = db.Column(db.Text)

    products = db.relationship('Product', backref='supplier', lazy=True)

    def __repr__(self):
        return f'<Supplier {self.nama}>'


class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(20), unique=True, nullable=False, index=True)
    nama_barang = db.Column(db.String(100), nullable=False)
    kategori = db.Column(db.String(50), nullable=False)
    stok = db.Column(db.Integer, nullable=False, default=0)
    harga = db.Column(db.Integer, nullable=False, default=0)
    min_stok = db.Column(db.Integer, nullable=False, default=10)
    lokasi_rak = db.Column(db.String(50))
    is_deleted = db.Column(db.Boolean, nullable=False, default=False, index=True)

    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'), nullable=True)

    movements = db.relationship('StockMovement', backref='product', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Product {self.sku} - {self.nama_barang}>'


class StockMovement(db.Model):
    __tablename__ = 'stock_movements'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    jumlah = db.Column(db.Integer, nullable=False)
    tipe = db.Column(db.String(20), nullable=False)
    keterangan = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship('User', backref='movements')

    def __repr__(self):
        return f'<StockMovement {self.tipe} {self.jumlah} for Product ID {self.product_id}>'
