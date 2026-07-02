from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SelectField, TextAreaField, SubmitField
from wtforms.validators import InputRequired, Length, EqualTo, NumberRange, ValidationError
from zenithstock.models import User, Product, Supplier


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[
        InputRequired(message="Username wajib diisi."),
        Length(min=4, max=50, message="Username harus antara 4 sampai 50 karakter.")
    ])
    password = PasswordField('Password', validators=[
        InputRequired(message="Password wajib diisi."),
        Length(min=6, message="Password minimal 6 karakter.")
    ])
    confirm_password = PasswordField('Konfirmasi Password', validators=[
        InputRequired(message="Konfirmasi password wajib diisi."),
        EqualTo('password', message="Password dan konfirmasi password tidak cocok.")
    ])
    role = SelectField(
        'Hak Akses / Peran',
        choices=[('staff', 'Staff Gudang'), ('admin', 'Administrator')],
        default='staff'
    )

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data.strip()).first()
        if user:
            raise ValidationError("Username sudah terdaftar. Silakan pilih username lain.")


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
        InputRequired(message="Username wajib diisi.")
    ])
    password = PasswordField('Password', validators=[
        InputRequired(message="Password wajib diisi.")
    ])


class ProductForm(FlaskForm):
    sku = StringField('SKU', validators=[
        InputRequired(message="SKU / Kode Barang wajib diisi."),
        Length(min=3, max=20, message="SKU harus antara 3 sampai 20 karakter.")
    ])
    nama_barang = StringField('Nama Barang', validators=[
        InputRequired(message="Nama barang wajib diisi."),
        Length(max=100, message="Nama barang tidak boleh melebihi 100 karakter.")
    ])
    kategori = StringField('Kategori', validators=[
        InputRequired(message="Kategori wajib diisi."),
        Length(max=50, message="Kategori tidak boleh melebihi 50 karakter.")
    ])
    stok = IntegerField('Stok Awal', validators=[
        InputRequired(message="Stok wajib diisi."),
        NumberRange(min=0, message="Stok tidak boleh bernilai negatif.")
    ])
    harga = IntegerField('Harga (Rp)', validators=[
        InputRequired(message="Harga wajib diisi."),
        NumberRange(min=0, message="Harga tidak boleh bernilai negatif.")
    ])
    min_stok = IntegerField('Minimal Stok (Batas Kritis)', validators=[
        InputRequired(message="Batas stok kritis wajib diisi."),
        NumberRange(min=0, message="Batas stok kritis tidak boleh bernilai negatif.")
    ], default=10)
    lokasi_rak = StringField('Lokasi Rak / Fisik', validators=[
        Length(max=50, message="Lokasi rak tidak boleh melebihi 50 karakter.")
    ])
    supplier_id = SelectField('Pemasok / Supplier', coerce=int, validators=[])

    def __init__(self, *args, **kwargs):
        self.product_id = kwargs.pop('product_id', None)
        super(ProductForm, self).__init__(*args, **kwargs)
        suppliers = Supplier.query.order_by(Supplier.nama).all()
        self.supplier_id.choices = [(-1, '-- Pilih Supplier --')] + [(s.id, s.nama) for s in suppliers]

    def validate_sku(self, sku):
        product = Product.query.filter_by(sku=sku.data.strip().upper()).first()
        if product:
            if self.product_id is None or product.id != self.product_id:
                raise ValidationError("SKU sudah terpakai oleh barang lain. Gunakan SKU yang unik.")


class SupplierForm(FlaskForm):
    nama = StringField('Nama Supplier / Perusahaan', validators=[
        InputRequired(message="Nama supplier wajib diisi."),
        Length(max=100, message="Nama tidak boleh melebihi 100 karakter.")
    ])
    kontak = StringField('Nama Person in Charge (PIC)', validators=[
        Length(max=100, message="Kontak tidak boleh melebihi 100 karakter.")
    ])
    telepon = StringField('Nomor Telepon', validators=[
        Length(max=30, message="Telepon tidak boleh melebihi 30 karakter.")
    ])
    alamat = TextAreaField('Alamat Lengkap', validators=[])

    def __init__(self, *args, **kwargs):
        self.supplier_id = kwargs.pop('supplier_id', None)
        super(SupplierForm, self).__init__(*args, **kwargs)

    def validate_nama(self, nama):
        sup = Supplier.query.filter_by(nama=nama.data.strip()).first()
        if sup:
            if self.supplier_id is None or sup.id != self.supplier_id:
                raise ValidationError("Supplier dengan nama tersebut sudah terdaftar.")


class StockMovementForm(FlaskForm):
    product_id = SelectField('Pilih Produk', coerce=int, validators=[
        InputRequired(message="Silakan pilih produk.")
    ])
    tipe = SelectField('Tipe Mutasi', choices=[
        ('MASUK', 'Barang Masuk (+)'),
        ('KELUAR', 'Barang Keluar (-)'),
        ('PENYESUAIAN', 'Penyesuaian Stok')
    ], validators=[
        InputRequired(message="Tipe transaksi wajib diisi.")
    ])
    arah_penyesuaian = SelectField('Arah Penyesuaian', choices=[
        ('tambah', 'Penambahan (+)'),
        ('kurang', 'Pengurangan (-)')
    ], default='tambah')
    jumlah = IntegerField('Jumlah / Qty', validators=[
        InputRequired(message="Jumlah mutasi wajib diisi."),
        NumberRange(min=1, message="Jumlah minimal adalah 1 unit.")
    ])
    keterangan = StringField('Keterangan / Memo', validators=[
        Length(max=255, message="Keterangan tidak boleh melebihi 255 karakter.")
    ])

    def __init__(self, *args, **kwargs):
        super(StockMovementForm, self).__init__(*args, **kwargs)
        products = Product.query.filter_by(is_deleted=False).order_by(Product.sku).all()
        self.product_id.choices = [
            (p.id, f"[{p.sku}] {p.nama_barang} (Stok saat ini: {p.stok})")
            for p in products
        ]
