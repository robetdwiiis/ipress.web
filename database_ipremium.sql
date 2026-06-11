-- ============================================================
--  DATABASE: ipremium_store
--  Deskripsi: Database toko reseller iPhone iPremium Store
--  Dibuat untuk: XAMPP / phpMyAdmin (MySQL)
--  Versi: 1.0
-- ============================================================

CREATE DATABASE IF NOT EXISTS `ipremium_store`
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE `ipremium_store`;

-- ============================================================
-- TABEL 1: pengguna
-- Menyimpan semua data akun pengguna:
--   - Owner / Admin toko
--   - Reseller
--   - Pembeli biasa
-- ============================================================
CREATE TABLE IF NOT EXISTS `pengguna` (
  `id`                INT            NOT NULL AUTO_INCREMENT,
  `username`          VARCHAR(150)   NOT NULL UNIQUE,
  `email`             VARCHAR(254)   NOT NULL,
  `password`          VARCHAR(128)   NOT NULL COMMENT 'Hash password (tidak plain text)',
  `nama_depan`        VARCHAR(150)   NOT NULL DEFAULT '',
  `nama_belakang`     VARCHAR(150)   NOT NULL DEFAULT '',
  `peran`             ENUM('OWNER','RESELLER','BUYER') NOT NULL DEFAULT 'BUYER'
                      COMMENT 'OWNER=Admin, RESELLER=Mitra, BUYER=Pembeli',
  `status_reseller`   ENUM('NONE','PENDING','APPROVED','REJECTED') NOT NULL DEFAULT 'NONE',
  `id_upline`         INT            NULL COMMENT 'ID reseller yang merekrut (sponsor)',
  `saldo_komisi`      DECIMAL(12,2)  NOT NULL DEFAULT 0.00 COMMENT 'Saldo dompet komisi',
  -- Profil
  `no_hp`             VARCHAR(15)    NOT NULL DEFAULT '',
  `alamat`            TEXT           NOT NULL DEFAULT '',
  `kota`              VARCHAR(100)   NOT NULL DEFAULT '',
  `kode_pos`          VARCHAR(10)    NOT NULL DEFAULT '',
  `foto_profil`       VARCHAR(255)   NULL,
  -- Info rekening bank (untuk penarikan komisi)
  `nama_bank`         VARCHAR(100)   NOT NULL DEFAULT '',
  `no_rekening`       VARCHAR(50)    NOT NULL DEFAULT '',
  -- Status akun
  `is_aktif`          TINYINT(1)     NOT NULL DEFAULT 1,
  `is_superuser`      TINYINT(1)     NOT NULL DEFAULT 0,
  `tanggal_daftar`    DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `terakhir_login`    DATETIME       NULL,
  PRIMARY KEY (`id`),
  KEY `idx_peran` (`peran`),
  KEY `idx_upline` (`id_upline`),
  CONSTRAINT `fk_pengguna_upline`
    FOREIGN KEY (`id_upline`) REFERENCES `pengguna`(`id`)
    ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Semua akun pengguna: Owner, Reseller, dan Pembeli';


-- ============================================================
-- TABEL 2: produk
-- Menyimpan katalog produk iPhone yang dijual
-- ============================================================
CREATE TABLE IF NOT EXISTS `produk` (
  `id`          INT            NOT NULL AUTO_INCREMENT,
  `nama`        VARCHAR(200)   NOT NULL,
  `deskripsi`   TEXT           NOT NULL,
  `harga`       DECIMAL(12,2)  NOT NULL,
  `stok`        INT UNSIGNED   NOT NULL DEFAULT 0,
  `gambar`      VARCHAR(255)   NULL COMMENT 'Path file gambar produk',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Katalog produk iPhone yang tersedia di toko';


-- ============================================================
-- TABEL 3: pesanan
-- Menyimpan setiap transaksi pembelian dari pembeli
-- ============================================================
CREATE TABLE IF NOT EXISTS `pesanan` (
  `id`                INT            NOT NULL AUTO_INCREMENT,
  `id_pembeli`        INT            NOT NULL COMMENT 'Siapa yang memesan',
  `id_produk`         INT            NOT NULL COMMENT 'Produk apa yang dipesan',
  `id_reseller`       INT            NULL COMMENT 'Reseller yang membawa pembeli (bisa kosong)',
  `jumlah`            INT UNSIGNED   NOT NULL DEFAULT 1,
  -- Detail harga
  `harga_dasar`       DECIMAL(12,2)  NOT NULL COMMENT 'Harga satuan produk saat dipesan',
  `total_harga`       DECIMAL(12,2)  NOT NULL COMMENT 'Total = harga x jumlah',
  `biaya_platform`    DECIMAL(10,2)  NOT NULL DEFAULT 0.00 COMMENT 'Potongan 1% untuk Owner',
  -- Pembayaran
  `metode_bayar`      ENUM('BANK_BCA','BANK_BRI','BANK_MANDIRI','QRIS')
                      NOT NULL DEFAULT 'BANK_BCA',
  `bukti_bayar`       VARCHAR(255)   NULL COMMENT 'Path foto bukti transfer',
  -- Status pesanan
  `status`            ENUM('PENDING','PAID','SHIPPED','COMPLETED','CANCELLED')
                      NOT NULL DEFAULT 'PENDING'
                      COMMENT 'PENDING=Menunggu, PAID=Disetujui, SHIPPED=Dikirim, COMPLETED=Selesai',
  -- Data pengiriman
  `nama_penerima`     VARCHAR(100)   NOT NULL DEFAULT '',
  `hp_penerima`       VARCHAR(20)    NOT NULL DEFAULT '',
  `alamat_kirim`      TEXT           NOT NULL DEFAULT '',
  `tanggal_pesan`     DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_pembeli`   (`id_pembeli`),
  KEY `idx_reseller`  (`id_reseller`),
  KEY `idx_produk`    (`id_produk`),
  KEY `idx_status`    (`status`),
  CONSTRAINT `fk_pesanan_pembeli`
    FOREIGN KEY (`id_pembeli`) REFERENCES `pengguna`(`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_pesanan_produk`
    FOREIGN KEY (`id_produk`)  REFERENCES `produk`(`id`)   ON DELETE CASCADE,
  CONSTRAINT `fk_pesanan_reseller`
    FOREIGN KEY (`id_reseller`) REFERENCES `pengguna`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Semua transaksi pesanan dari pembeli';


-- ============================================================
-- TABEL 4: komisi
-- Riwayat komisi yang diterima oleh reseller dan owner
-- ============================================================
CREATE TABLE IF NOT EXISTS `komisi` (
  `id`              INT            NOT NULL AUTO_INCREMENT,
  `id_pengguna`     INT            NOT NULL COMMENT 'Siapa yang menerima komisi',
  `id_pesanan`      INT            NOT NULL COMMENT 'Dari pesanan mana',
  `jumlah`          DECIMAL(10,2)  NOT NULL,
  `keterangan`      VARCHAR(255)   NOT NULL COMMENT 'Contoh: Komisi Tier 1 (5%) dari Pesanan #12',
  `tanggal`         DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_pengguna` (`id_pengguna`),
  KEY `idx_pesanan`  (`id_pesanan`),
  CONSTRAINT `fk_komisi_pengguna`
    FOREIGN KEY (`id_pengguna`) REFERENCES `pengguna`(`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_komisi_pesanan`
    FOREIGN KEY (`id_pesanan`)  REFERENCES `pesanan`(`id`)  ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Log/riwayat komisi yang masuk ke dompet reseller dan owner';


-- ============================================================
-- TABEL 5: penarikan_dana
-- Pengajuan pencairan komisi oleh reseller
-- ============================================================
CREATE TABLE IF NOT EXISTS `penarikan_dana` (
  `id`              INT            NOT NULL AUTO_INCREMENT,
  `id_reseller`     INT            NOT NULL COMMENT 'Reseller yang mengajukan penarikan',
  `jumlah`          DECIMAL(12,2)  NOT NULL,
  `nama_bank`       VARCHAR(50)    NOT NULL,
  `no_rekening`     VARCHAR(50)    NOT NULL,
  `nama_rekening`   VARCHAR(100)   NOT NULL,
  `status`          ENUM('PENDING','APPROVED','REJECTED')
                    NOT NULL DEFAULT 'PENDING'
                    COMMENT 'PENDING=Menunggu, APPROVED=Sudah ditransfer, REJECTED=Ditolak',
  `tanggal_ajuan`   DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `tanggal_update`  DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_reseller` (`id_reseller`),
  KEY `idx_status`   (`status`),
  CONSTRAINT `fk_penarikan_reseller`
    FOREIGN KEY (`id_reseller`) REFERENCES `pengguna`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Riwayat pengajuan pencairan komisi oleh reseller';


-- ============================================================
-- TABEL 6: pengajuan_reseller
-- Formulir pendaftaran menjadi reseller
-- ============================================================
CREATE TABLE IF NOT EXISTS `pengajuan_reseller` (
  `id`              INT            NOT NULL AUTO_INCREMENT,
  `id_pengguna`     INT            NOT NULL COMMENT 'Pembeli yang mengajukan jadi reseller',
  `link_sosmed`     VARCHAR(200)   NOT NULL DEFAULT '' COMMENT 'Instagram, TikTok, dll',
  `rencana_pasarkan` TEXT          NOT NULL COMMENT 'Rencana pemasaran produk',
  `status`          ENUM('PENDING','APPROVED','REJECTED')
                    NOT NULL DEFAULT 'PENDING',
  `tanggal_ajuan`   DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_pengguna` (`id_pengguna`),
  KEY `idx_status`   (`status`),
  CONSTRAINT `fk_pengajuan_pengguna`
    FOREIGN KEY (`id_pengguna`) REFERENCES `pengguna`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Formulir pendaftaran menjadi reseller yang dikirim pembeli';


-- ============================================================
-- TABEL 7: pesan_kontak
-- Pesan dari halaman Hubungi Kami + balasan admin
-- ============================================================
CREATE TABLE IF NOT EXISTS `pesan_kontak` (
  `id`            INT          NOT NULL AUTO_INCREMENT,
  `id_pengguna`   INT          NULL COMMENT 'Jika pengirim sudah login (bisa NULL jika tamu)',
  `nama`          VARCHAR(100) NOT NULL,
  `email`         VARCHAR(254) NOT NULL,
  `topik`         VARCHAR(200) NOT NULL,
  `isi_pesan`     TEXT         NOT NULL,
  `sudah_dibaca`  TINYINT(1)   NOT NULL DEFAULT 0 COMMENT '0=Belum dibaca, 1=Sudah dibaca',
  `balasan_admin` TEXT         NULL COMMENT 'Isi balasan dari admin',
  `tanggal_balas` DATETIME     NULL,
  `tanggal_kirim` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_pengguna`    (`id_pengguna`),
  KEY `idx_sudah_dibaca` (`sudah_dibaca`),
  CONSTRAINT `fk_pesan_pengguna`
    FOREIGN KEY (`id_pengguna`) REFERENCES `pengguna`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Pesan masuk dari halaman Hubungi Kami beserta balasan admin';


-- ============================================================
-- DATA CONTOH (SAMPLE DATA)
-- Hapus bagian ini jika tidak dibutuhkan
-- ============================================================

-- Contoh 1 akun Owner/Admin
INSERT INTO `pengguna`
  (`username`, `email`, `password`, `nama_depan`, `peran`, `is_superuser`, `is_aktif`)
VALUES
  ('admin', 'admin@ipremium.id', '[hash_password_disini]', 'Admin', 'OWNER', 1, 1);

-- Contoh produk iPhone
INSERT INTO `produk` (`nama`, `deskripsi`, `harga`, `stok`) VALUES
  ('iPhone 15 Pro Max 256GB', 'iPhone 15 Pro Max Natural Titanium 256GB, garansi resmi Apple Indonesia 1 tahun', 21999000.00, 10),
  ('iPhone 15 Pro 128GB',     'iPhone 15 Pro Black Titanium 128GB, garansi resmi Apple Indonesia 1 tahun',      18499000.00, 15),
  ('iPhone 15 128GB',         'iPhone 15 Pink 128GB, garansi resmi Apple Indonesia 1 tahun',                    14999000.00, 20),
  ('iPhone 14 128GB',         'iPhone 14 Midnight 128GB, garansi resmi Apple Indonesia 1 tahun',                11999000.00, 8),
  ('iPhone 13 128GB',         'iPhone 13 Starlight 128GB, garansi resmi Apple Indonesia 1 tahun',                9499000.00, 5);


-- ============================================================
-- RINGKASAN TABEL
-- ============================================================
-- pengguna         → Semua akun (Admin, Reseller, Pembeli)
-- produk           → Katalog produk iPhone
-- pesanan          → Semua transaksi pembelian
-- komisi           → Log komisi masuk ke dompet
-- penarikan_dana   → Pengajuan cairkan komisi
-- pengajuan_reseller → Formulir daftar jadi reseller
-- pesan_kontak     → Pesan dari halaman Hubungi Kami
-- ============================================================
