




### 1. Visi, Tujuan, dan Identitas Proyek

* **Nama Sistem:** ZenithStock (Sistem Manajemen Inventaris Barang).
* **Tujuan Utama:** Mengembangkan aplikasi sistem informasi sederhana berbasis web untuk mengelola, melacak, dan memonitor pergerakan stok barang secara *real-time*. Sistem ini dirancang untuk mencegah kehilangan data, memblokir duplikasi barang, dan memastikan hanya pihak berwenang yang bisa mengubah data inventaris.


* **Target Rilis:** Sebelum 4 Juli 2026 pukul 23.59 WIB.



### 2. Tech Stack & Framework (Fondasi Teknologi)

Kita akan menggunakan ekosistem Python modern sesuai standar tugas, dipadukan dengan desain *frontend* yang elegan:

* **Backend (Core Logic):** **Flask**. Kita gunakan Flask karena sifatnya yang *micro-framework*. Ringan, modular, dan memberi kita kontrol penuh atas arsitektur *routing* (GET/POST).


* **Database & ORM:** **SQLite** dibungkus dengan **Flask-SQLAlchemy**. Kita tidak akan menulis SQL manual. Semuanya menggunakan *Object-Relational Mapping* (ORM).


* **Frontend Engine:** **Jinja2** untuk *template engine*.


* **UI/UX Framework:** **Tailwind CSS** (via CDN). Kita akan membangun UI *dark-mode* modern (mirip referensi di tugas). Jauh lebih rapi dan dinamis daripada Bootstrap standar.



### 3. Arsitektur Folder & Separation of Concerns

Rubrik meminta struktur kode yang rapi dan memisahkan logika program dengan tampilan. Ini adalah arsitektur yang akan kita bangun:

```text
/zenithstock_project
├── app.py              # Jantung aplikasi: Inisialisasi Flask, Config DB, & Error Handlers[cite: 1]
├── models.py           # Layer Data (OOP): Definisi Class User & Class Barang[cite: 1]
├── routes.py           # Layer Controller: Logika bisnis, validasi form, & CRUD[cite: 1]
├── requirements.txt    # Daftar dependensi (Flask, SQLAlchemy, dll)
├── /static             # Aset Statis[cite: 1]
│   ├── /css            # Custom CSS jika Tailwind butuh penyesuaian
│   └── /img            # Logo dan aset gambar
└── /templates          # Layer View (Jinja2)[cite: 1]
    ├── base.html       # Induk template (Navbar, Sidebar, Layout utama)[cite: 1]
    ├── welcome.html    # Halaman Landing Page (UI Modern sebelum login)
    ├── /auth           # register.html, login.html[cite: 1]
    └── /dashboard      # index.html, create.html, edit.html (Operasi CRUD)[cite: 1]

```

### 4. Bedah Algoritma & Implementasi OOP (Object-Oriented Programming)

Ini adalah jantung dari penilaian tugas. Kita mengimplementasikan OOP murni di `models.py`.

* Konsep Class dan Object:
Tabel *database* tidak dibuat manual, melainkan melalui *Class*.


* `Class User`: Memiliki atribut seperti `id`, `username`, `password_hash`.
* `Class Product`: Memiliki atribut seperti `id`, `sku` (kode barang), `nama_barang`, `kategori`, `stok`, dan `harga`.


* Algoritma Database (SQLAlchemy):
Saat kita menambah data, kita tidak memakai `INSERT INTO`. Kita membuat instansi *object* baru:
`barang_baru = Product(sku='ITM-001', nama='Laptop', stok=10)`
Lalu disimpan dengan algoritma komit SQLAlchemy: `db.session.add(barang_baru)` lalu `db.session.commit()`.



### 5. Alur Kerja Sistem (End-to-End Workflow)

Ini adalah urutan logika (*state*) dari sistem kita, dari user membuka web hingga *logout*:

1. **Welcome Page (Titik Masuk):** User membuka web. Disambut dengan UI/UX yang modern, *clean*, dengan animasi halus Tailwind. Hanya ada tombol "Login" atau "Register".
2. Autentikasi (Gerbang Keamanan):


* **Register:** Form meminta `username` dan `password`. Algoritma kita menangkap form dengan `request.form`. Password **wajib di-hash** (diacak) menggunakan *library* keamanan.


* **Login:** User memasukkan data. Algoritma mencocokkan *hash* di *database*. Jika valid, sistem membuat *Session*.
* **Route Protection:** Jika user mencoba mengetik URL `/dashboard` tanpa login, algoritma *Route Guard* akan memblokir dan menendangnya kembali ke halaman login.




3. Dashboard Utama:


* Setelah login, masuk ke Dashboard. Menampilkan sapaan "Welcome, [Nama User]" (menampilkan informasi pengguna yang login).


* Di sebelah kiri ada menu navigasi (Dashboard, Tambah Barang, Daftar Barang, Logout).




4. Operasi CRUD (Inti Aplikasi):


* **Create (Tambah Data):** User mengisi form. Algoritma melakukan validasi ketat (lihat poin 6). Jika lolos, simpan ke database.


* **Read (Menampilkan Data):** Query seluruh data dari SQLite menggunakan `Product.query.all()`, lalu dikirim ke tabel di Jinja2.


* **Update (Ubah Data):** Form terisi otomatis dengan data lama, user bisa mengubah stok/nama. Disimpan kembali ke ID yang sama.


* **Delete (Hapus Data):** Tombol bahaya. Algoritma akan mencari produk berdasarkan ID, lalu mengeksekusi `db.session.delete()`.




5. Logout: Sesi dihancurkan, kembali ke Welcome Page.



### 6. Algoritma Form Handling & Validasi (Anti-Sampah)

Sebagai *engineer*, kita tidak boleh membiarkan data sampah masuk ke database. Sesuai syarat, form kita punya pertahanan 3 lapis:

* **Validasi Field Wajib:** Di level HTML ditambahkan atribut `required`. Di level backend, ada pengecekan `if not username` atau `if not nama_barang`.


* **Validasi Tipe Data:** Jika atribut stok butuh *integer* (angka), namun diisi dengan huruf, backend akan menolak dengan blok *Try-Except* di Python dan mengembalikan pesan *error*.


* **Algoritma Pencegah Duplikasi:** Sebelum merekam data baru, sistem mencari apakah `SKU` atau `Username` sudah ada di database. Jika ada, proses dibatalkan: `Product.query.filter_by(sku=input_sku).first()`.



### 7. Strategi Jinja2 & UI/UX

Untuk mendapatkan nilai A pada struktur tampilan:

* Kita bangun `base.html` sebagai induk yang berisi tag `<html>`, `<head>`, tautan ke Tailwind CSS, *Navbar*, dan *Sidebar*.
* Di tengah `base.html`, kita letakkan `{% block content %}{% endblock %}`.


* File lain seperti `dashboard.html` hanya perlu menulis `{% extends 'base.html' %}` di baris pertama. Ini memangkas redundansi kode hingga 60%, memastikan aplikasi sangat ringan dan mudah di-*maintain*.







