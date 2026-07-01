# ZenithStock Enterprise – Sistem Manajemen Inventaris Industri Modern

Selamat datang di **ZenithStock Enterprise**, sebuah sistem informasi manajemen inventaris pergudangan modern skala industri berbasis web. Aplikasi ini dirancang secara khusus untuk membantu memantau, melacak, dan memonitor pergerakan stok barang secara *real-time* guna mencegah ketidaksesuaian stok, memblokir pencatatan duplikasi barang, serta menerapkan sistem keamanan otorisasi akses yang ketat.

---

## 1. Penjelasan Umum Project

### Nama Project
* **ZenithStock Enterprise** (Sistem Manajemen Inventaris Barang Pabrik & Gudang Industri).

### Studi Kasus
Pada pergudangan industri berskala menengah hingga besar, sering kali terjadi masalah kritis seperti:
* Hilangnya riwayat transaksi barang masuk dan keluar (tidak adanya sistem audit log).
* Inkonsistensi jumlah stok fisik dengan stok digital (data stok bocor).
* Akses data yang terlalu bebas bagi semua karyawan tanpa batasan wewenang.
* Duplikasi kode barang (SKU) yang menyebabkan kekacauan data.

**ZenithStock Enterprise** hadir untuk menyelesaikan masalah di atas dengan mengimplementasikan pencatatan mutasi permanen (*Audit Trail*), membatasi akses fitur menggunakan *Role-Based Access Control* (RBAC), mencegah input barang ganda dengan validasi SKU unik, serta menampilkan performa pergudangan lewat dashboard analitik visual.

### Fitur-Fitur Utama Aplikasi
1. **Dashboard Manajemen Barang (CRUD):** Tambah, ubah, tampilkan, dan hapus data produk pergudangan dengan aman.
2. **Pencatatan Mutasi Stok Real-Time:** Mencatat barang masuk, keluar, dan penyesuaian stok secara otomatis.
3. **Log Audit Trail Permanen:** Riwayat aktivitas mutasi yang tercatat permanen di database tanpa celah penghapusan oleh user mana pun.
4. **Keamanan Multi-Role (RBAC):** Pembatasan hak akses penuh untuk **Admin** (memiliki akses CRUD user, supplier, barang, log audit) dan **Staff** (akses operasional pencatatan barang).
5. **Dashboard Analitik Terintegrasi:** Menyajikan grafik tren mutasi 14 hari, grafik donat status kesehatan stok, grafik batang valuasi per kategori, dan komposisi transaksi menggunakan Chart.js.
6. **Manajemen Pemasok / Vendor:** Pengelolaan database mitra logistik untuk ketepatan rantai pengadaan logistik barang.
7. **Antarmuka Responsif & Premium:** UI bertema Dark Mode dengan desain responsif penuh (ramah perangkat mobile/HP maupun desktop).

---

## 2. Struktur Folder Project

Aplikasi ini menggunakan pola desain modular (Blueprint) pada framework Flask, memisahkan logika program (Controller), representasi database (Model), dan tampilan web (View).

```text
/ZenithStock
├── app.py                  # Entry-point utama: Menjalankan server Flask
├── requirements.txt        # Daftar dependensi modul Python (Flask, SQLAlchemy, dll)
├── seed_all.py             # Script database seeder untuk data demo relistis
├── zenithstock/            # Package utama aplikasi
│   ├── __init__.py         # Inisialisasi Flask, DB, Session Login, & database seeding
│   ├── models.py           # Layer Data (OOP): Definisi tabel database dan relasi
│   ├── forms.py            # Form Class & Validasi Input (Flask-WTF)
│   ├── /routes             # Layer Controller: Logika bisnis dan routing blueprint
│   │   ├── auth.py         # Routing autentikasi (login, register, logout)
│   │   ├── dashboard.py    # Routing CRUD Barang & Inventaris Utama
│   │   ├── movements.py    # Routing transaksi mutasi stok barang
│   │   ├── suppliers.py    # Routing CRUD Supplier / Vendor
│   │   ├── analytics.py    # Routing kalkulasi data statistik & chart
│   │   ├── audit.py        # Routing pembacaan log audit trail
│   │   └── users.py        # Routing manajemen user (khusus admin)
│   ├── /static             # Aset Statis program
│   │   ├── /css            # File stylesheet custom (style.css)
│   │   └── /img            # File gambar logo dan latar belakang
│   └── /templates          # Layer View (Template Jinja2)
│       ├── base.html       # Induk layout utama web (Navbar & Sidebar)
│       ├── welcome.html    # Halaman landing page sebelum login
│       ├── /auth           # Template halaman login, register, base_auth
│       ├── /dashboard      # Template halaman daftar inventaris (index, create, edit)
│       ├── /movements      # Template halaman mutasi stok
│       ├── /suppliers      # Template halaman supplier
│       ├── /analytics      # Halaman visualisasi statistik
│       ├── /audit          # Halaman tabel audit trail
│       ├── /users          # Halaman manajemen pengguna
│       └── /errors         # Template penanganan halaman error (404, 403, 500)
```

### Database yang Digunakan
* **SQLite:** Database relasional berbasis file lokal yang diletakkan dalam direktori `instance/zenithstock.db`. Dikelola langsung melalui **Flask-SQLAlchemy (ORM)** tanpa perlu penulisan query SQL mentah manual.

---

## 3. Penjelasan Implementasi Teknis Detail

### a. Routing Flask (Blueprint & HTTP Methods)
Aplikasi memisahkan endpoint rute web menggunakan **Flask Blueprint** agar kode tetap rapi dan terorganisir.
* **GET Method:** Digunakan untuk meminta/mengambil data dari server untuk ditampilkan ke pengguna. (Contoh: menampilkan tabel barang, membuka halaman form kosong).
* **POST Method:** Digunakan untuk mengirimkan data sensitif atau data baru hasil input pengguna ke server untuk diproses. (Contoh: memvalidasi formulir login, menyimpan barang baru, memperbarui mutasi).

**Contoh Implementasi Routing:**
```python
# Rute untuk merender form tambah barang (GET) dan menyimpan datanya (POST)
@dashboard_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = ProductForm()
    if request.method == 'POST' and form.validate_on_submit():
        # Memproses data form di sini
        return redirect(url_for('dashboard.index'))
    return render_template('dashboard/create.html', form=form)
```

---

### b. Form Handling dan Validation
Pengambilan dan penyaringan data yang diinput oleh pengguna diproteksi dengan 3 lapis keamanan:
1. **Flask-WTF:** Form didefinisikan sebagai Class di Python (`forms.py`) yang secara otomatis mengaitkan proteksi token **CSRF** (*Cross-Site Request Forgery*) untuk mencegah serangan pembajakan sesi.
2. **Pengambilan Data Form:** Nilai input diambil menggunakan properti form WTF seperti `form.nama_barang.data` atau secara mentah via `request.form.get('nama_field')`.
3. **Validasi Input yang Diterapkan:**
   * **Data Required:** Field penting wajib diisi (tidak boleh kosong).
   * **Type Casting & Range:** Validasi bahwa stok dan harga harus berupa angka positif.
   * **Keunikan SKU & Username:** Pengecekan ke database sebelum menyimpan untuk memastikan tidak ada SKU produk atau Username pengguna yang duplikat.

---

### c. Database dan SQLAlchemy (OOP)
Pola interaksi database dikelola secara penuh menggunakan pemrograman berorientasi objek (OOP) melalui **SQLAlchemy ORM**.

#### Model Class yang Dibuat (`models.py`)
1. **User (Tabel `users`):** Mengelola kredensial masuk pengguna. Atribut: `id`, `username`, `password_hash`, `role` (admin/staff).
2. **Product (Tabel `products`):** Data inventaris barang. Atribut: `id`, `sku` (unik), `nama_barang`, `kategori`, `stok`, `harga`, `min_stok` (batas stok kritis), `lokasi_rak`, `supplier_id`.
3. **Supplier (Tabel `suppliers`):** Kontak vendor pemasok. Atribut: `id`, `nama` (unik), `kontak`, `telepon`, `alamat`.
4. **StockMovement (Tabel `stock_movements`):** Log riwayat mutasi. Atribut: `id`, `product_id`, `user_id`, `jumlah` (positif = masuk, negatif = keluar), `tipe`, `keterangan`, `created_at`.

#### Operasi CRUD Database dengan SQLAlchemy
* **Create (Simpan Data Baru):**
  ```python
  baru = Product(sku='ELK-01', nama_barang='Keyboard', stok=10, harga=100000)
  db.session.add(baru)
  db.session.commit()
  ```
* **Read (Mengambil Data):**
  ```python
  # Ambil semua data produk
  semua_produk = Product.query.all()
  # Cari produk berdasarkan filter spesifik
  produk_kritis = Product.query.filter(Product.stok <= Product.min_stok).all()
  ```
* **Update (Ubah Data):**
  ```python
  produk = Product.query.get(id_barang)
  produk.harga = 120000
  db.session.commit()
  ```
* **Delete (Hapus Data):**
  ```python
  produk_hapus = Product.query.get(id_barang)
  db.session.delete(produk_hapus)
  db.session.commit()
  ```

---

### d. Template Jinja2 (Inheritance & DRY Principle)
Tampilan web dibuat sangat efisien menggunakan mesin template **Jinja2** dengan menerapkan konsep pewarisan (*Template Inheritance*).

* **`base.html` (Template Induk):** Berisi fondasi kerangka HTML dasar, pemanggilan CDN Tailwind CSS, master stylesheet `style.css`, navigasi Sidebar, navigasi Topbar, dan area penampung notifikasi Flash (Toast alert).
* **`{% extends "base.html" %}`:** Ditulis di baris pertama template anak (seperti `dashboard/index.html` atau `suppliers/index.html`) untuk menyalin seluruh struktur kerangka navigasi dari `base.html`.
* **`{% block content %}`:** Wadah penampung yang akan diisi secara dinamis oleh halaman anak. Template induk `base.html` hanya memanggil `{% block content %}{% endblock %}`, lalu halaman anak mendefinisikan isinya di dalam tag block yang sama.
* **Keuntungan:** Meminimalkan redundansi kode (prinsip DRY - *Don't Repeat Yourself*). Mengubah navigasi atau footer cukup dilakukan sekali di `base.html`, dan otomatis diterapkan ke puluhan halaman lainnya.

---

### e. Authentication & Route Protection (Keamanan Sesi)
Fitur autentikasi ditangani secara aman dengan modul **Flask-Login** dan enkripsi password mutakhir.

* **Proses Register:** Mengambil data username dan password baru. Sebelum disimpan ke database, password **wajib dienkripsi** (diacak) menggunakan pustaka `werkzeug.security.generate_password_hash` untuk memastikan kerahasiaan data sekalipun file database bocor.
* **Proses Login:** Mengambil username dan password ketikan user. Sistem mencocokkan hash password di database menggunakan `check_password_hash`. Jika cocok, Flask-Login menginisiasi login sesi (`login_user(user)`).
* **Proses Logout:** Mengakhiri sesi pengguna aktif dan menghancurkan cookie sesi dengan perintah `logout_user()`, lalu mengembalikan pengguna ke landing page.
* **Pembatasan Halaman (Route Protection):**
  * Rute operasional diproteksi dengan decorator `@login_required` sehingga pengguna yang belum login akan langsung ditendang kembali ke login page dengan pesan peringatan.
  * Fitur sensitif (seperti hapus barang, CRUD user admin, lihat log audit penuh) diperketat dengan validasi peran:
    ```python
    if not current_user.is_admin():
        abort(403) # Menolak akses dengan status Forbidden
    ```

---

## 4. Tim Pengembang (Developers)

* **Lead Developer:** Tasya Nabila
* **Junior Developer:** Gempur Budi Anarki
