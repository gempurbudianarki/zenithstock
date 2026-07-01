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
    
    print("Creating default and realistic users...")
    # Active Admins
    admin = User(username='admin', role='admin', status='active')
    admin.set_password('admin123')
    db.session.add(admin)
    
    rina = User(username='rina_admin', role='admin', status='active')
    rina.set_password('rina123')
    db.session.add(rina)

    # Active Staff
    staff = User(username='staff', role='staff', status='active')
    staff.set_password('staff123')
    db.session.add(staff)

    budi = User(username='budi_logistics', role='staff', status='active')
    budi.set_password('budi123')
    db.session.add(budi)

    ani = User(username='ani_gudang', role='staff', status='active')
    ani.set_password('ani123')
    db.session.add(ani)

    # Pending Staff (Menunggu Persetujuan Admin)
    iwan = User(username='iwan_logistik', role='staff', status='pending')
    iwan.set_password('iwan123')
    db.session.add(iwan)

    siti = User(username='siti_operasional', role='staff', status='pending')
    siti.set_password('siti123')
    db.session.add(siti)

    # Inactive Staff (Dinonaktifkan)
    joko = User(username='joko_penjualan', role='staff', status='inactive')
    joko.set_password('joko123')
    db.session.add(joko)

    doni = User(username='doni_staff', role='staff', status='inactive')
    doni.set_password('doni123')
    db.session.add(doni)

    db.session.commit()
    
    print("Creating suppliers/vendors...")
    suppliers_data = [
        ("PT Global Elektronika", "Hendra", "021-889900", "Kawasan Industri Jababeka, Bekasi"),
        ("CV Berkah Stationary", "Siti Aminah", "0812-3456-789", "Jl. Margonda Raya No. 45, Depok"),
        ("PT Suku Cadang Utama", "Andi Wijaya", "021-554433", "Ruko Mega Glodok Kemayoran, Jakarta Pusat"),
        ("CV Kimia Nusantara", "Dr. Rahmat", "022-776655", "Kawasan Industri Gedebage, Bandung"),
        ("PT Semen Nusantara", "Bagus", "021-998877", "Gresik, Jawa Timur"),
        ("CV Jaya Logistik", "Aris", "0813-5566-7788", "Jl. Pemuda No. 12, Surabaya"),
        ("PT Tekno Presisi", "Rian", "021-443322", "Kawasan Industri Cikarang, Bekasi")
    ]
    
    supplier_objects = []
    for nama, pic, telp, alamat in suppliers_data:
        sup = Supplier(nama=nama, kontak=pic, telepon=telp, alamat=alamat)
        db.session.add(sup)
        supplier_objects.append(sup)
    db.session.commit()
    
    print("Creating products...")
    # (SKU, Nama, Kategori, Stok Awal, Harga, Min Stok, Lokasi Rak, Supplier)
    products_data = [
        # Elektronik (PT Global Elektronika / PT Tekno Presisi)
        ("ELK-ASU-01", "Laptop ASUS VivoBook 14", "Elektronik", 18, 8500000, 5, "Rak-A1", "PT Global Elektronika"),
        ("ELK-LOG-02", "Mouse Wireless Logitech M220", "Elektronik", 55, 185000, 10, "Rak-A3", "PT Global Elektronika"),
        ("ELK-SAM-03", "SSD Samsung EVO 980 1TB", "Elektronik", 30, 1450000, 8, "Rak-A2", "PT Global Elektronika"),
        ("ELK-KEY-04", "Keyboard Mechanical Keychron K2", "Elektronik", 4, 1200000, 5, "Rak-A4", "PT Global Elektronika"), # Kritis
        ("ELK-MON-05", "Monitor LG UltraWide 29\"", "Elektronik", 0, 3200000, 3, "Rak-A5", "PT Global Elektronika"), # Habis
        ("ELK-ROU-06", "Router TP-Link Archer AX55 WiFi 6", "Elektronik", 12, 950000, 4, "Rak-A6", "PT Tekno Presisi"),
        
        # Alat Tulis (CV Berkah Stationary)
        ("ATK-PAP-01", "Kertas HVS Sinar Dunia A4 80g", "Alat Tulis", 140, 48000, 20, "Rak-B1", "CV Berkah Stationary"),
        ("ATK-PEN-02", "Pulpen Gel Pilot G2 Box (12 pcs)", "Alat Tulis", 40, 150000, 8, "Rak-B2", "CV Berkah Stationary"),
        ("ATK-MAR-03", "Spidol Snowman Boardmarker Black", "Alat Tulis", 8, 95000, 15, "Rak-B3", "CV Berkah Stationary"), # Kritis
        ("ATK-NOT-04", "Buku Catatan Spiral Kiky A5", "Alat Tulis", 65, 12000, 10, "Rak-B4", "CV Berkah Stationary"),
        ("ATK-FOL-05", "Map Snelhechter Plastik (50 pcs)", "Alat Tulis", 15, 75000, 5, "Rak-B5", "CV Berkah Stationary"),
        
        # Suku Cadang (PT Suku Cadang Utama)
        ("SPC-BLT-01", "Baut Baja Hex M12 x 50mm (100 pcs)", "Suku Cadang", 180, 250000, 30, "Rak-C1", "PT Suku Cadang Utama"),
        ("SPC-BRG-02", "Bearing Ball NSK 6204ZZ", "Suku Cadang", 95, 45000, 15, "Rak-C2", "PT Suku Cadang Utama"),
        ("SPC-FIL-03", "Filter Oli Denso Avanza", "Suku Cadang", 3, 35000, 10, "Rak-C3", "PT Suku Cadang Utama"), # Kritis
        ("SPC-BEL-04", "V-Belt Mitsuboshi A-38", "Suku Cadang", 0, 65000, 5, "Rak-C4", "PT Suku Cadang Utama"), # Habis
        ("SPC-GIR-05", "Gear Chain Set Honda Supra Fit", "Suku Cadang", 16, 210000, 4, "Rak-C5", "PT Suku Cadang Utama"),
        
        # Bahan Kimia (CV Kimia Nusantara)
        ("CHM-IPA-01", "Alkohol Isopropil 99% (5 Liter)", "Bahan Kimia", 22, 175000, 5, "Gudang-Kimia", "CV Kimia Nusantara"),
        ("CHM-SLG-02", "Silica Gel Desiccant Blue 1kg", "Bahan Kimia", 48, 60000, 10, "Gudang-Kimia", "CV Kimia Nusantara"),
        ("CHM-LUB-03", "Pelumas WD-40 Anti Karat 412ml", "Bahan Kimia", 25, 72000, 5, "Rak-D1", "CV Kimia Nusantara"),
        ("CHM-ACL-04", "Asam Klorida HCl 35% (1 Liter)", "Bahan Kimia", 2, 45000, 5, "Gudang-Kimia", "CV Kimia Nusantara"), # Kritis
        
        # Bahan Konstruksi (PT Semen Nusantara / CV Jaya Logistik)
        ("KNS-SEM-01", "Semen Tiga Roda Portland 50kg", "Bahan Konstruksi", 250, 72000, 40, "Gudang-B", "PT Semen Nusantara"),
        ("KNS-BTA-02", "Bata Ringan Hebel (per Kubik)", "Bahan Konstruksi", 14, 680000, 5, "Gudang-B", "CV Jaya Logistik"),
        ("KNS-CAT-03", "Cat Tembok Nippon Paint Weatherbond 20L", "Bahan Konstruksi", 0, 1450000, 2, "Gudang-B", "CV Jaya Logistik"), # Habis
        
        # Alat Safety (CV Jaya Logistik / PT Tekno Presisi)
        ("SAF-HLM-01", "Helm Proyek Safety MSA Putih", "Alat Safety", 35, 125000, 8, "Rak-E1", "CV Jaya Logistik"),
        ("SAF-GLV-02", "Sarung Tangan Las Kulit 14\"", "Alat Safety", 70, 45000, 15, "Rak-E2", "CV Jaya Logistik"),
        ("SAF-EXT-03", "Tabung Pemadam Api APAR CO2 5kg", "Alat Safety", 5, 620000, 6, "Rak-E3", "PT Tekno Presisi"), # Kritis
        ("SAF-MSK-04", "Masker Respirator 3M Double Filter", "Alat Safety", 18, 220000, 5, "Rak-E4", "PT Tekno Presisi"),
        ("SAF-SKT-05", "Sepatu Safety Krisbow Gladiator 6\"", "Alat Safety", 2, 480000, 5, "Rak-E5", "PT Tekno Presisi") # Kritis
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
    
    print("Creating dynamic and dense historic stock movements (100+ transactions)...")
    now = datetime.now()
    active_users = [admin, rina, staff, budi, ani]
    
    # 1. Establish baseline initial stock entries (all MASUK) for all products
    for sku, prod in product_objects.items():
        # Set initial stock level (which is current stock + some historic exits)
        baseline = prod.stok + random.randint(15, 60)
        day_offset = random.randint(24, 30)
        baseline_date = now - timedelta(days=day_offset)
        
        m_base = StockMovement(
            product_id=prod.id,
            user_id=random.choice(active_users).id,
            jumlah=baseline,
            tipe='MASUK',
            keterangan='Penyetoran awal inventaris baru',
            created_at=baseline_date
        )
        db.session.add(m_base)
        
        # Update internal simulation stock tracking
        prod.sim_stock = baseline
        
    db.session.commit()
    
    # 2. Simulate historical entries and exits over 25 days
    sim_movements = []
    reasons_keluar = [
        "Distribusi bahan baku divisi produksi",
        "Pengambilan logistik lapangan proyek",
        "Permintaan suku cadang pengganti",
        "Penjualan ritel retail outlet",
        "Penyaluran berkala gudang cabang",
        "Pengeluaran unit uji laboratorium"
    ]
    
    reasons_masuk = [
        "Pengiriman ulang restock dari supplier",
        "Retur barang lebih dari divisi lapangan",
        "Penyetoran berkala kuartalan",
        "Penerimaan logistik log baru",
        "Pembelian material darurat"
    ]
    
    for i in range(105):
        # Choose a random day in the past (1 to 23 days ago)
        day_offset = random.randint(1, 23)
        movement_date = now - timedelta(days=day_offset)
        
        prod = random.choice(list(product_objects.values()))
        tipe = random.choice(['MASUK', 'KELUAR', 'PENYESUAIAN'])
        
        # Calculate quantity based on type
        if tipe == 'MASUK':
            qty = random.randint(5, 30)
            keterangan = random.choice(reasons_masuk)
            prod.sim_stock += qty
        elif tipe == 'KELUAR':
            qty = random.randint(3, 20)
            # Prevent going into negative too deep during simulation
            if prod.sim_stock - qty < 0:
                qty = prod.sim_stock
            if qty == 0:
                # If currently 0, do a MASUK instead
                qty = random.randint(10, 20)
                tipe = 'MASUK'
                keterangan = "Pengisian darurat stok kosong"
                prod.sim_stock += qty
            else:
                prod.sim_stock -= qty
                qty = -qty
                keterangan = random.choice(reasons_keluar)
        else: # PENYESUAIAN
            qty = random.choice([-3, -2, -1, 1, 2, 3])
            keterangan = f"Opname fisik koreksi selisih kartu (koreksi {qty} unit)"
            prod.sim_stock += qty
            
        m = StockMovement(
            product_id=prod.id,
            user_id=random.choice(active_users).id,
            jumlah=qty,
            tipe=tipe,
            keterangan=keterangan,
            created_at=movement_date
        )
        db.session.add(m)
        
    db.session.commit()
    
    # 3. Apply final adjustment to bridge simulated stock with exact current seeded DB stock
    for sku, prod in product_objects.items():
        diff = prod.stok - prod.sim_stock
        if diff != 0:
            # Add one final adjustment entry to align model stok with simulation history
            m_adj = StockMovement(
                product_id=prod.id,
                user_id=random.choice(active_users).id,
                jumlah=diff,
                tipe='PENYESUAIAN',
                keterangan='Penyesuaian akhir rekonsiliasi stok sistem',
                created_at=now - timedelta(hours=random.randint(1, 12))
            )
            db.session.add(m_adj)
            
    db.session.commit()
    print("Database successfully seeded with highly detailed, large-scale dataset!")
