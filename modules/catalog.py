from utils.database import (bacaJSON, tambahData, cariData, ubahData, hapusData, simpanJSON,
                            fileKategori, fileProduk, fileRental, filePaket)
from utils.helpers import (formatRupiah, ubahTanggal, tanggalKeTeks, hariIni,
                           periodeBertabrakan, statusAktif)
from utils.display import (cetakJudul, cetakMenu, pesanBerhasil, pesanGagal,
                           pesanInfo, tampilkanTabel, tungguEnter)
from utils.validation import (inputTeks, inputAngka, inputYaTidak, inputPilihanMenu, cekAkses)


# ---------- STOK ----------

def hitungTersedia(kodeProduk, tanggalMulai, tanggalAkhir):
    # stok fisik dikurangi barang pada transaksi aktif yang periodenya bertabrakan
    produk = cariData(fileProduk, 'kode', kodeProduk)
    if produk is None:
        return 0
    mulai = ubahTanggal(tanggalMulai)
    akhir = ubahTanggal(tanggalAkhir)
    dipakai = 0

    for rental in bacaJSON(fileRental):
        if rental['statusRental'] not in statusAktif:
            continue
        mulaiRental = ubahTanggal(rental['tanggalMulai'])
        akhirRental = ubahTanggal(rental['tanggalAkhir'])
        # barang yang belum kembali tetap dianggap terpakai sampai hari ini
        if rental['statusRental'] in ('ST-03', 'ST-04') and hariIni() > akhirRental:
            akhirRental = hariIni()
        if not periodeBertabrakan(mulai, akhir, mulaiRental, akhirRental):
            continue
        for item in rental['items']:
            if item['kodeProduk'] == kodeProduk:
                dipakai += item['jumlah']

    sisa = produk['stok'] - dipakai
    if sisa < 0:
        sisa = 0
    return sisa


def hitungJumlahStatus(kodeProduk, daftarStatus):
    # jumlah barang pada transaksi dengan status tertentu (untuk laporan stok)
    jumlah = 0
    for rental in bacaJSON(fileRental):
        if rental['statusRental'] in daftarStatus:
            for item in rental['items']:
                if item['kodeProduk'] == kodeProduk:
                    jumlah += item['jumlah']
    return jumlah


# ---------- TAMPILAN KATALOG ----------

def namaLengkapProduk(produk):
    nama = produk['nama']
    if produk['jenis'] != '':
        nama = nama + ' (' + produk['jenis'] + ')'
    return nama


def tampilkanTabelProduk(daftarProduk):
    baris = []
    hari = tanggalKeTeks(hariIni())
    for produk in daftarProduk:
        if produk['aktif']:
            aktif = 'Ya'
        else:
            aktif = 'Tidak'
        tersedia = hitungTersedia(produk['kode'], hari, hari)
        baris.append([produk['kode'], namaLengkapProduk(produk), produk['warna'],
                      produk['ukuran'], formatRupiah(produk['harga']),
                      produk['stok'], tersedia, aktif])
    tampilkanTabel(['Kode', 'Nama', 'Warna', 'Ukuran', 'Harga/Hari', 'Stok', 'Sedia', 'Aktif'],
                   baris, ('Harga/Hari', 'Stok', 'Sedia'))


def tampilkanSemuaProduk():
    dataProduk = bacaJSON(fileProduk)
    tampilkanTabelProduk(dataProduk)
    print(f'\n{len(dataProduk)} variasi produk berhasil ditampilkan.')
    print('Keterangan: Stok = stok fisik, Sedia = tersedia hari ini.')


def tampilkanDetailProduk(produk):
    kategori = cariData(fileKategori, 'kode', produk['kategori'])
    if kategori is None:
        namaKategori = produk['kategori']
    else:
        namaKategori = kategori['nama']
    hari = tanggalKeTeks(hariIni())

    cetakJudul('DETAIL BARANG')
    print(f'Kode          : {produk["kode"]}')
    print(f'Nama          : {namaLengkapProduk(produk)}')
    print(f'Kategori      : {namaKategori} ({produk["kategori"]})')
    print(f'Warna         : {produk["warna"]}')
    print(f'Ukuran        : {produk["ukuran"]}')
    if produk['keterangan'] != '':
        print(f'Keterangan    : {produk["keterangan"]}')
    print(f'Harga sewa    : {formatRupiah(produk["harga"])} per hari')
    print(f'Stok fisik    : {produk["stok"]}')
    print(f'Tersedia      : {hitungTersedia(produk["kode"], hari, hari)} (hari ini)')
    if produk['aktif']:
        print('Status        : Aktif')
    else:
        print('Status        : Nonaktif')


def show_categories():
    dataProduk = bacaJSON(fileProduk)
    baris = []
    for kategori in bacaJSON(fileKategori):
        jumlah = 0
        for produk in dataProduk:
            if produk['kategori'] == kategori['kode']:
                jumlah += 1
        baris.append([kategori['kode'], kategori['nama'], jumlah])
    tampilkanTabel(['Kode', 'Kategori', 'Jumlah Variasi'], baris, ('Jumlah Variasi',))


def show_catalog():
    # Flowchart halaman 4 (D)
    while True:
        cetakJudul('KATALOG RUPAÉ - KATEGORI')
        show_categories()
        kodeKategori = input('\nMasukkan kode kategori (0 = kembali): ').strip().upper()
        if kodeKategori == '0':
            return
        kategori = cariData(fileKategori, 'kode', kodeKategori)
        if kategori is None:
            pesanGagal('Kode kategori tidak valid!')
            continue

        daftarProduk = []
        for produk in bacaJSON(fileProduk):
            if produk['kategori'] == kodeKategori:
                daftarProduk.append(produk)

        while True:
            cetakJudul(f'KATALOG - {kategori["nama"].upper()}')
            tampilkanTabelProduk(daftarProduk)
            kodeBarang = input('\nMasukkan kode barang (0 = pilih kategori lagi): ').strip().upper()
            if kodeBarang == '0':
                break
            produk = cariData(fileProduk, 'kode', kodeBarang)
            if produk is None or produk['kategori'] != kodeKategori:
                pesanGagal('Kode barang tidak valid!')
                continue
            tampilkanDetailProduk(produk)
            return


# ---------- CRUD KATEGORI ----------

def add_category():
    cetakJudul('TAMBAH KATEGORI')
    kode = inputTeks('Kode kategori (contoh KAT-008, 0 = batal): ').upper()
    if kode == '0':
        return
    if cariData(fileKategori, 'kode', kode) is not None:
        pesanGagal('Kode kategori sudah digunakan!')
        return
    nama = inputTeks('Nama kategori: ')
    tambahData(fileKategori, {'kode': kode, 'nama': nama})
    pesanBerhasil('Kategori berhasil ditambahkan.')


def update_category():
    cetakJudul('UBAH KATEGORI')
    show_categories()
    kode = inputTeks('Kode kategori (0 = batal): ').upper()
    if kode == '0':
        return
    kategori = cariData(fileKategori, 'kode', kode)
    if kategori is None:
        pesanGagal('Kode kategori tidak ditemukan!')
        return
    kategori['nama'] = inputTeks(f'Nama baru (saat ini {kategori["nama"]}): ')
    ubahData(fileKategori, 'kode', kode, kategori)
    pesanBerhasil('Kategori berhasil diubah.')


def delete_category():
    cetakJudul('HAPUS KATEGORI')
    show_categories()
    kode = inputTeks('Kode kategori (0 = batal): ').upper()
    if kode == '0':
        return
    if cariData(fileKategori, 'kode', kode) is None:
        pesanGagal('Kode kategori tidak ditemukan!')
        return
    for produk in bacaJSON(fileProduk):
        if produk['kategori'] == kode:
            pesanGagal('Kategori tidak dapat dihapus karena masih memiliki produk!')
            return
    if inputYaTidak('Yakin hapus kategori ini? (y/n): '):
        hapusData(fileKategori, 'kode', kode)
        pesanBerhasil('Kategori berhasil dihapus.')
    else:
        pesanInfo('Penghapusan dibatalkan.')


def manage_categories(user):
    if not cekAkses(user, ('Admin',)):
        return
    while True:
        cetakJudul('KELOLA KATEGORI')
        cetakMenu(['1. Tambah', '2. Ubah', '3. Hapus', '4. Lihat', '0. Kembali'])
        pilihan = inputPilihanMenu('Pilih menu: ', ('1', '2', '3', '4', '0'))
        if pilihan == '0':
            return
        elif pilihan == '1':
            add_category()
        elif pilihan == '2':
            update_category()
        elif pilihan == '3':
            delete_category()
        else:
            cetakJudul('DAFTAR KATEGORI')
            show_categories()
        tungguEnter()


# ---------- CRUD PRODUK ----------

def inputHargaOpsional(pesan):
    # kosong = belum dikonfigurasi (None)
    while True:
        teks = input(pesan).strip()
        if teks == '':
            return None
        try:
            harga = int(teks)
            if harga <= 0:
                pesanGagal('Harga harus lebih dari 0!')
            else:
                return harga
        except ValueError:
            pesanGagal('Harga harus berupa angka!')


def add_product():
    cetakJudul('TAMBAH PRODUK')
    kode = inputTeks('Kode produk (0 = batal): ').upper()
    if kode == '0':
        return
    if cariData(fileProduk, 'kode', kode) is not None:
        pesanGagal('Kode produk sudah digunakan!')
        return
    show_categories()
    kodeKategori = inputTeks('Kode kategori: ').upper()
    if cariData(fileKategori, 'kode', kodeKategori) is None:
        pesanGagal('Kategori tidak ditemukan! Produk harus memiliki kategori.')
        return

    nama = inputTeks('Nama produk: ')
    warna = input('Warna (kosong = -): ').strip()
    ukuran = input('Ukuran (kosong = -): ').strip()
    jenis = input('Jenis kelamin/jenis (kosong = tidak ada): ').strip()
    keterangan = input('Keterangan (kosong = tidak ada): ').strip()
    harga = inputHargaOpsional('Harga sewa per hari (kosong = belum diatur): ')
    stok = inputAngka('Stok: ', 0)

    if warna == '':
        warna = '-'
    if ukuran == '':
        ukuran = '-'
    produk = {'kode': kode, 'nama': nama, 'kategori': kodeKategori, 'warna': warna,
              'ukuran': ukuran, 'jenis': jenis, 'keterangan': keterangan,
              'harga': harga, 'stok': stok, 'aktif': True}
    tambahData(fileProduk, produk)
    pesanBerhasil('Produk berhasil ditambahkan.')


def pilihProduk(judul):
    # menampilkan semua produk lalu meminta kode; None jika batal
    cetakJudul(judul)
    tampilkanSemuaProduk()
    kode = inputTeks('Kode produk (0 = batal): ').upper()
    if kode == '0':
        return None
    produk = cariData(fileProduk, 'kode', kode)
    if produk is None:
        pesanGagal('Kode produk tidak ditemukan!')
    return produk


def update_product():
    produk = pilihProduk('UBAH INFORMASI PRODUK')
    if produk is None:
        return
    print('Kosongkan input jika tidak ingin mengubah.')
    nama = input(f'Nama ({produk["nama"]}): ').strip()
    warna = input(f'Warna ({produk["warna"]}): ').strip()
    ukuran = input(f'Ukuran ({produk["ukuran"]}): ').strip()
    keterangan = input(f'Keterangan ({produk["keterangan"]}): ').strip()
    if nama != '':
        produk['nama'] = nama
    if warna != '':
        produk['warna'] = warna
    if ukuran != '':
        produk['ukuran'] = ukuran
    if keterangan != '':
        produk['keterangan'] = keterangan
    ubahData(fileProduk, 'kode', produk['kode'], produk)
    pesanBerhasil('Informasi produk berhasil diubah.')


def set_price_stock():
    produk = pilihProduk('ATUR HARGA DAN STOK')
    if produk is None:
        return
    print(f'Harga saat ini: {formatRupiah(produk["harga"])} | Stok saat ini: {produk["stok"]}')
    harga = inputHargaOpsional('Harga baru per hari (kosong = tidak diubah): ')
    stokBaru = input('Stok baru (kosong = tidak diubah): ').strip()
    if harga is not None:
        produk['harga'] = harga
    if stokBaru != '':
        try:
            stok = int(stokBaru)
            if stok < 0:
                pesanGagal('Stok tidak boleh negatif!')
                return
            produk['stok'] = stok
        except ValueError:
            pesanGagal('Stok harus berupa angka!')
            return
    ubahData(fileProduk, 'kode', produk['kode'], produk)
    pesanBerhasil('Harga dan stok berhasil disimpan.')


def set_category_price():
    cetakJudul('ATUR HARGA SATU KATEGORI')
    show_categories()
    kode = inputTeks('Kode kategori (0 = batal): ').upper()
    if kode == '0':
        return
    if cariData(fileKategori, 'kode', kode) is None:
        pesanGagal('Kategori tidak ditemukan!')
        return
    harga = inputAngka('Harga sewa per hari untuk semua produk kategori ini: ', 1)
    dataProduk = bacaJSON(fileProduk)
    jumlah = 0
    for produk in dataProduk:
        if produk['kategori'] == kode:
            produk['harga'] = harga
            jumlah += 1
    simpanJSON(fileProduk, dataProduk)
    pesanBerhasil(f'Harga {formatRupiah(harga)} diterapkan pada {jumlah} produk.')


def toggle_product():
    produk = pilihProduk('AKTIFKAN/NONAKTIFKAN PRODUK')
    if produk is None:
        return
    produk['aktif'] = not produk['aktif']
    ubahData(fileProduk, 'kode', produk['kode'], produk)
    if produk['aktif']:
        pesanBerhasil('Produk diaktifkan.')
    else:
        pesanBerhasil('Produk dinonaktifkan. Produk tidak dapat disewa untuk pesanan baru.')


def delete_product():
    produk = pilihProduk('HAPUS PRODUK')
    if produk is None:
        return
    for rental in bacaJSON(fileRental):
        if rental['statusRental'] in statusAktif:
            for item in rental['items']:
                if item['kodeProduk'] == produk['kode']:
                    pesanGagal(f'Produk masih ada di transaksi aktif {rental["kode"]}. Tidak boleh dihapus!')
                    return
    for paket in bacaJSON(filePaket):
        for slot in paket['komposisi']:
            if produk['kode'] in slot['pilihan']:
                pesanGagal(f'Produk dipakai di paket {paket["kode"]}. Ubah paket terlebih dahulu!')
                return
    if inputYaTidak('Yakin hapus produk ini? (y/n): '):
        hapusData(fileProduk, 'kode', produk['kode'])
        pesanBerhasil('Produk berhasil dihapus.')
    else:
        pesanInfo('Penghapusan dibatalkan.')


def search_products():
    cetakJudul('CARI PRODUK')
    kataKunci = inputTeks('Kata kunci (kode/nama/warna): ').lower()
    hasil = []
    for produk in bacaJSON(fileProduk):
        teks = (produk['kode'] + ' ' + produk['nama'] + ' ' + produk['warna']).lower()
        if kataKunci in teks:
            hasil.append(produk)
    if len(hasil) == 0:
        pesanGagal('Produk tidak ditemukan!')
    else:
        tampilkanTabelProduk(hasil)


def manage_products(user):
    if not cekAkses(user, ('Admin',)):
        return
    while True:
        cetakJudul('KELOLA KATALOG')
        cetakMenu(['1. Tambah Produk', '2. Ubah Informasi Produk', '3. Atur Harga dan Stok',
                   '4. Aktifkan/Nonaktifkan Produk', '5. Hapus Produk',
                   '6. Lihat Semua Produk', '7. Cari Produk',
                   '8. Atur Harga Satu Kategori', '0. Kembali'])
        pilihan = inputPilihanMenu('Pilih menu: ', ('1', '2', '3', '4', '5', '6', '7', '8', '0'))
        if pilihan == '0':
            return
        elif pilihan == '1':
            add_product()
        elif pilihan == '2':
            update_product()
        elif pilihan == '3':
            set_price_stock()
        elif pilihan == '4':
            toggle_product()
        elif pilihan == '5':
            delete_product()
        elif pilihan == '6':
            cetakJudul('KATALOG LENGKAP RUPAÉ')
            tampilkanSemuaProduk()
        elif pilihan == '7':
            search_products()
        else:
            set_category_price()
        tungguEnter()
