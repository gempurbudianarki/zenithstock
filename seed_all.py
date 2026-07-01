import os
from datetime import datetime, timedelta
import random
from zenithstock import create_app, db
from zenithstock.models import User, Supplier, Product, StockMovement

app = create_app()

with app.app_context():
    print("Clearing database...")
    db.session.query(StockMovement).delete()
    db.session.query(Product).delete()
    db.session.query(Supplier).delete()
    db.session.query(User).delete()
    db.session.commit()
    
    print("Creating default users...")
    admin = User(username='admin', role='admin', status='active')
    admin.set_password('admin123')
    db.session.add(admin)
    
    staff = User(username='staff', role='staff', status='active')
    staff.set_password('staff123')
    db.session.add(staff)
    
    db.session.commit()
    
    print("Creating suppliers...")
    suppliers = [
        Supplier(nama="PT Global Elektronika", kontak="Hendra", telepon="021-889900", alamat="Kawasan Industri Jababeka, Bekasi"),
        Supplier(nama="CV Berkah Stationary", kontak="Siti Aminah", telepon="0812-3456-789", alamat="Jl. Margonda Raya No. 45, Depok"),
        Supplier(nama="PT Suku Cadang Utama", kontak="Andi Wijaya", telepon="021-554433", alamat="Ruko Mega Glodok Kemayoran, Jakarta Pusat"),
        Supplier(nama="CV Kimia Nusantara", kontak="Dr. Rahmat", telepon="022-776655", alamat="Kawasan Industri Gedebage, Bandung")
    ]
    for s in suppliers:
        db.session.add(s)
    db.session.commit()
    
    print("Creating products...")
    products_data = [
        # Elektronik
        ("ELK-ASU-01", "Laptop ASUS VivoBook 14", "Elektronik", 15, 8500000, 5, "Rak-A1", "PT Global Elektronika"),
        ("ELK-LOG-02", "Mouse Wireless Logitech M220", "Elektronik", 45, 185000, 10, "Rak-A3", "PT Global Elektronika"),
        ("ELK-SAM-03", "SSD Samsung EVO 980 1TB", "Elektronik", 25, 1450000, 8, "Rak-A2", "PT Global Elektronika"),
        ("ELK-KEY-04", "Keyboard Mechanical Keychron K2", "Elektronik", 4, 1200000, 5, "Rak-A4", "PT Global Elektronika"), # Kritis
        ("ELK-MON-05", "Monitor LG UltraWide 29\"", "Elektronik", 0, 3200000, 3, "Rak-A5", "PT Global Elektronika"), # Habis
        
        # Alat Tulis
        ("ATK-PAP-01", "Kertas HVS Sinar Dunia A4 80g", "Alat Tulis", 120, 48000, 20, "Rak-B1", "CV Berkah Stationary"),
        ("ATK-PEN-02", "Pulpen Gel Pilot G2 Box (12 pcs)", "Alat Tulis", 35, 150000, 8, "Rak-B2", "CV Berkah Stationary"),
        ("ATK-MAR-03", "Spidol Snowman Boardmarker Black", "Alat Tulis", 8, 95000, 15, "Rak-B3", "CV Berkah Stationary"), # Kritis
        ("ATK-NOT-04", "Buku Catatan Spiral Kiky A5", "Alat Tulis", 60, 12000, 10, "Rak-B4", "CV Berkah Stationary"),
        
        # Suku Cadang
        ("SPC-BLT-01", "Baut Baja Hex M12 x 50mm (100 pcs)", "Suku Cadang", 150, 250000, 30, "Rak-C1", "PT Suku Cadang Utama"),
        ("SPC-BRG-02", "Bearing Ball NSK 6204ZZ", "Suku Cadang", 80, 45000, 15, "Rak-C2", "PT Suku Cadang Utama"),
        ("SPC-FIL-03", "Filter Oli Denso Avanza", "Suku Cadang", 3, 35000, 10, "Rak-C3", "PT Suku Cadang Utama"), # Kritis
        ("SPC-BEL-04", "V-Belt Mitsuboshi A-38", "Suku Cadang", 0, 65000, 5, "Rak-C4", "PT Suku Cadang Utama"), # Habis
        
        # Bahan Kimia
        ("CHM-IPA-01", "Alkohol Isopropil 99% (5 Liter)", "Bahan Kimia", 18, 175000, 5, "Gudang-Kimia", "CV Kimia Nusantara"),
        ("CHM-SLG-02", "Silica Gel Desiccant Blue 1kg", "Bahan Kimia", 40, 60000, 10, "Gudang-Kimia", "CV Kimia Nusantara"),
        ("CHM-LUB-03", "Pelumas WD-40 Anti Karat 412ml", "Bahan Kimia", 22, 72000, 5, "Rak-D1", "CV Kimia Nusantara")
    ]
    
    product_objects = {}
    for p_sku, p_name, p_cat, p_stok, p_harga, p_min, p_rak, s_name in products_data:
        sup = Supplier.query.filter_by(nama=s_name).first()
        prod = Product(
            sku=p_sku,
            nama_barang=p_name,
            kategori=p_cat,
            stok=p_stok,
            harga=p_harga,
            min_stok=p_min,
            lokasi_rak=p_rak,
            supplier_id=sup.id if sup else None
        )
        db.session.add(prod)
        product_objects[p_sku] = prod
        
    db.session.commit()
    
    print("Creating historical stock movements...")
    now = datetime.now()
    users = [admin, staff]
    
    for sku, prod in product_objects.items():
        if prod.stok > 0:
            init_qty = prod.stok + random.randint(5, 20)
            day_offset = random.randint(8, 13)
            movement_date = now - timedelta(days=day_offset)
            m1 = StockMovement(
                product_id=prod.id,
                user_id=random.choice(users).id,
                jumlah=init_qty,
                tipe='MASUK',
                keterangan='Stok awal registrasi gudang',
                created_at=movement_date
            )
            db.session.add(m1)
            
            out_qty = init_qty - prod.stok
            if out_qty > 0:
                day_offset_out = random.randint(1, 7)
                movement_date_out = now - timedelta(days=day_offset_out)
                m2 = StockMovement(
                    product_id=prod.id,
                    user_id=random.choice(users).id,
                    jumlah=-out_qty,
                    tipe='KELUAR',
                    keterangan='Pengeluaran divisi operasional',
                    created_at=movement_date_out
                )
                db.session.add(m2)
        else:
            init_qty = random.randint(5, 10)
            day_offset_in = random.randint(10, 13)
            m1 = StockMovement(
                product_id=prod.id,
                user_id=random.choice(users).id,
                jumlah=init_qty,
                tipe='MASUK',
                keterangan='Stok awal',
                created_at=now - timedelta(days=day_offset_in)
            )
            db.session.add(m1)
            
            day_offset_out = random.randint(2, 5)
            m2 = StockMovement(
                product_id=prod.id,
                user_id=random.choice(users).id,
                jumlah=-init_qty,
                tipe='KELUAR',
                keterangan='Barang diambil unit produksi',
                created_at=now - timedelta(days=day_offset_out)
            )
            db.session.add(m2)
            
    # Add extra random daily movements
    for i in range(25):
        day_offset = random.randint(0, 13)
        m_date = now - timedelta(days=day_offset)
        prod = random.choice(list(product_objects.values()))
        tipe = random.choice(['MASUK', 'KELUAR', 'PENYESUAIAN'])
        qty = random.randint(1, 10)
        
        if tipe == 'KELUAR':
            qty = -qty
        elif tipe == 'PENYESUAIAN':
            qty = random.choice([-2, -1, 1, 2])
            
        m = StockMovement(
            product_id=prod.id,
            user_id=random.choice(users).id,
            jumlah=qty,
            tipe=tipe,
            keterangan=f'Transaksi harian batch {i+1}',
            created_at=m_date
        )
        db.session.add(m)

    db.session.commit()
    print("Database successfully seeded with realistic history!")
