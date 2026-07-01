# 🌌 ZenithStock Enterprise
### *Sistem Informasi Manajemen Logistik & Inventaris Industri Real-Time*

---

## 📖 Analisis Kasus & Penjelasan Umum

Dalam industri manufaktur dan distribusi skala besar, **manajemen gudang** sering kali menemui tantangan fatal yang berdampak langsung pada kerugian finansial. Beberapa permasalahan utama meliputi:

* **Penyusutan Aset (Stock Shrinkage):** Kehilangan unit barang akibat tidak adanya pencatatan transaksi yang permanen dan transparan.
* **Redundansi Kode (Data Redundancy):** Penginputan kode SKU (*Stock Keeping Unit*) yang ganda sehingga merusak database inventaris.
* **Kebocoran Wewenang:** Tindakan manipulasi harga atau stok oleh pihak operasional yang tidak memiliki otoritas otorisasi.
* **Kelambatan Keputusan:** Pengambilan keputusan yang terhambat karena tidak adanya data agregat visual tentang total nilai aset dan volume stok terkini.

**ZenithStock Enterprise** hadir sebagai solusi komprehensif. Sistem ini dibangun untuk menegakkan **Integritas Data** dan **Keamanan Transaksi**. Dengan mengotomatisasi setiap perubahan stok ke dalam log yang bersifat *immutable* (tidak bisa dihapus), ZenithStock memastikan setiap pergerakan barang terdokumentasi secara transparan dan akuntabel.

---

## 🛠️ Arsitektur & Struktur Folder Project

Aplikasi ini dibangun menggunakan arsitektur **MVC (Model-View-Controller)** yang terpisah dengan modul-modul fungsional (**Flask Blueprint**). Struktur direktori diorganisasikan agar bersih dan modular:

```text
📁 ZenithStock
│
├── 📄 app.py                  # Entry point aplikasi (Inisialisasi server & port)
├── 📄 requirements.txt        # Dependensi pustaka Python pendukung
├── 📄 seed_all.py             # Script otomatisasi seeding data demonstrasi
│
└── 📁 zenithstock/            # Package utama aplikasi
    ├── 📄 __init__.py         # Inisialisasi app, db ORM, CSRF, & login manager
    ├── 📄 models.py           # Layer Data (OOP): Definisi relasi database & tabel
    ├── 📄 forms.py            # Layer Validasi: Class validasi formulir (Flask-WTF)
    │
    ├── 📁 routes/             # Layer Controller (Blueprints)
    │   ├── 📄 auth.py         # Autentikasi keamanan user (login, register, logout)
    │   ├── 📄 dashboard.py    # Logika CRUD produk/barang utama
    │   ├── 📄 movements.py    # Manajemen pencatatan aliran transaksi stok
    │   ├── 📄 suppliers.py    # Logika CRUD supplier/vendor logistik
    │   ├── 📄 analytics.py    # Pengolahan kalkulasi data analitik & grafik
    │   ├── 📄 audit.py        # Log audit trail keamanan transaksi
    │   └── 📄 users.py        # Otorisasi manajemen user (khusus Admin)
    │
    ├── 📁 static/             # Aset Statis Aplikasi
    │   ├── 📁 css/            # Lembar gaya visual utama (style.css)
    │   └── 📁 img/            # Media logo dan latar belakang dinamis
    │
    └── 📁 templates/          # Layer View (Template Jinja2)
        ├── 📄 base.html       # Kerangka dasar induk web (Sidebar & Header)
        ├── 📄 welcome.html    # Landing page responsif modern sebelum masuk sistem
        ├── 📁 auth/           # Formulir login dan registrasi akun
        ├── 📁 dashboard/      # Tabel utama inventaris dan form CRUD barang
        ├── 📁 movements/      # Form catat mutasi transaksi barang masuk/keluar
        ├── 📁 suppliers/      # Panel CRUD mitra pemasok/vendor
        ├── 📁 analytics/      # Visualisasi analitik grafik kinerja gudang
        ├── 📁 audit/          # Lembar pantau riwayat mutasi komprehensif
        ├── 📁 users/          # Lembar manajemen akun staff gudang
        └── 📁 errors/         # Penanganan respon HTTP error (403, 404, 500)
```

---

## 🎯 Penjelasan Implementasi Fondasi Sistem

Sistem informasi ZenithStock Enterprise telah dirancang dan diimplementasikan dengan memenuhi seluruh pilar rekayasa perangkat lunak web modern:

### 1. Framework Utama (Flask)
Aplikasi menggunakan **Flask** sebagai mesin backend. Desain modulnya menerapkan sistem **Blueprint** untuk membagi rute berdasarkan tanggung jawab logika masing-masing kelas kontroler:
* **Fungsi Rute (Routing):** Mengatur pemetaan URL/endpoint agar mengarah ke fungsi eksekusi yang tepat di Python.
* **HTTP Method handling (GET & POST):**
  * **GET:** Digunakan untuk me-render halaman, meminta data dari server, dan memuat form.
  * **POST:** Digunakan untuk mengirimkan data input dari formulir secara aman (enkripsi data di layer HTTP) guna melakukan registrasi, login, pembuatan produk, penambahan stok, dll.

---

### 2. Antarmuka Dinamis & Pewarisan (Template Engine Jinja2)
Visualisasi web menggunakan **Jinja2** yang menerapkan prinsip pewarisan terpusat (*Inheritance*) guna mewujudkan kode yang bersih (*Clean Code/DRY*):
* **`base.html` sebagai Parent Template:** Berisi kerangka global halaman (impor Tailwind CSS, inisialisasi Alpine.js untuk drop-down, sidebar dinamis, dan header).
* **`extends` dan `block`:** File anak (misal: halaman daftar barang) hanya perlu menulis `{% extends "base.html" %}` dan menuliskan isinya di dalam tag `{% block content %}`.
* **Dynamic Rendering:** Data dari database dievaluasi secara dinamis menggunakan kondisional `{% if %}`, perulangan `{% for %}`, dan filter format angka/harga (mata uang Rupiah).

---

### 3. Keamanan Input & Anti-Duplikasi (Form Handling & Validation)
Setiap data masukan yang dikirim oleh pengguna disaring ketat sebelum masuk ke memori database:
* **Token CSRF (Flask-WTF):** Setiap form wajib menyertakan token enkripsi CSRF untuk memvalidasi bahwa data dikirim dari formulir resmi aplikasi, bukan hasil injeksi pihak ketiga.
* **Validasi Tipe Data & Range:** Memastikan input kuantitas stok dan nilai harga harus bertipe integer/float positif. Jika ada input huruf pada kolom angka, sistem secara otomatis menolak dan memunculkan pesan error.
* **Validasi Keunikan Database:** Sebelum mendaftarkan barang baru, sistem mencocokkan kode SKU ke database untuk memastikan tidak ada duplikasi kode identitas barang.

---

### 4. Manajemen Objek Database (SQLAlchemy ORM)
Interaksi dengan SQLite dikelola secara murni lewat paradigma OOP (Object-Oriented Programming) menggunakan **SQLAlchemy**. Kita mendefinisikan tabel dalam bentuk **Class Model** dan atribut sebagai objek kolom database.

#### Model Relasi Data (`models.py`)
* **User (Tabel `users`):** Berisi username, password_hash, dan role.
* **Supplier (Tabel `suppliers`):** Berisi profil vendor. Berelasi *one-to-many* ke tabel Product.
* **Product (Tabel `products`):** Berisi data produk (SKU, nama, stok, harga, min_stok). Memiliki foreign key ke tabel Supplier dan berelasi *one-to-many* ke StockMovement.
* **StockMovement (Tabel `stock_movements`):** Log mutasi. Memiliki foreign key ke tabel Product dan User untuk melacak siapa petugas yang memicu mutasi.

#### Penerapan Siklus CRUD
* **Create:** Membuat instansi objek baru dari class Model (misal: `Product(...)`), menyimpannya menggunakan `db.session.add(produk)`, lalu menulisnya secara fisik ke file database dengan `db.session.commit()`.
* **Read:** Menampilkan data menggunakan pencarian objek seperti `Product.query.all()` atau pencarian filter spesifik `Product.query.filter_by(sku=input_sku).first()`.
* **Update:** Memuat objek berdasarkan id, memodifikasi nilai atribut secara langsung di python, lalu menyimpannya kembali dengan `db.session.commit()`.
* **Delete:** Melakukan penghapusan fisik record data produk melalui perintah `db.session.delete(produk_objektif)` yang juga secara otomatis menghapus mutasi terkait secara berantai (*cascade deletion*).

---

### 5. Otentikasi & Otorisasi Sistem Keamanan (Authentication & Authorization)
Sistem membatasi akses fitur secara berlapis untuk menjamin keamanan aset data:
* **Otentikasi (Siapa Anda):**
  * **Register:** Enkripsi password menggunakan algoritma hash modern `generate_password_hash` sebelum disimpan ke database (tidak ada penyimpanan plain-text password).
  * **Login:** Autentikasi dengan pencocokan hash password `check_password_hash` dan pengelolaan sesi oleh `Flask-Login` via `login_user`.
  * **Logout:** Mengakhiri sesi pengguna aktif dan menghancurkan cookie sesi dengan perintah `logout_user()`, lalu mengembalikan pengguna ke landing page.
  * **Sesi Aktif (@login_required):** Mencegah pengguna tidak sah melihat halaman dalam sistem jika belum terotentikasi.
* **Otorisasi (Apa yang Boleh Anda Lakukan):**
  * Membagi hak akses sistem menjadi 2 level: **Administrator** (Admin) dan **Staff**.
  * Pengguna non-admin (Staff) secara otomatis dibatasi dan tidak dapat mengakses rute manajemen pengguna (users CRUD) dan log audit log trail penuh. Upaya bypass URL manual akan langsung menghasilkan status HTTP **403 Forbidden**.

---

## 🚀 Panduan Menjalankan Project

### Langkah 1: Kloning & Persiapan Dependensi
Pastikan Python telah terpasang di komputer Anda. Buka terminal di folder project, lalu jalankan perintah instalasi dependensi:
```bash
pip install -r requirements.txt
```

### Langkah 2: Lakukan Seeding Database (Data Demo)
Jalankan seeder database untuk otomatis membersihkan tabel dan membuat data suplai barang & riwayat mutasi yang melimpah secara otomatis:
```bash
python seed_all.py
```

### Langkah 3: Jalankan Server Aplikasi
Mulai server Flask lokal:
```bash
python app.py
```
Buka browser Anda dan akses tautan **[http://127.0.0.1:5000/](http://127.0.0.1:5000/)**.

---

## 👥 Tim Pengembang (Developer Team)

Sistem ZenithStock Enterprise dirancang, dianalisis, dan dikembangkan secara mandiri oleh:

* **Developer:** Gempur Budi Anarki
