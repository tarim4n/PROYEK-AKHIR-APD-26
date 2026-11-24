from utils.database import (bacaJSON, tambahData, cariData, ubahData, hapusData,
                            filePaket, fileProduk, fileMUA, fileRental)
from utils.helpers import formatRupiah, generateKode, statusAktif
from utils.display import (cetakJudul, cetakMenu, pesanBerhasil, pesanGagal,
                           pesanInfo, tampilkanTabel, tungguEnter)
from utils.validation import (inputTeks, inputYaTidak, inputPilihanMenu, cekAkses)


def komposisiTeks(paket):
    bagian = []
    for slot in paket['komposisi']:
        bagian.append(slot['label'])
    teks = ' + '.join(bagian)
    layanan = cariData(fileMUA, 'kode', paket['mua'])
    if layanan is not None:
        teks = teks + ' + 1 MUA ' + layanan['nama']
    return teks


def show_packages():
    baris = []
    for paket in bacaJSON(filePaket):
        if paket['aktif']:
            status = 'Aktif'
        else:
            status = 'Nonaktif'
        baris.append([paket['kode'], paket['nama'], komposisiTeks(paket), status])
    tampilkanTabel(['Kode', 'Nama Paket', 'Komposisi', 'Status'], baris)


def tampilkanOpsi(daftarKode):
    baris = []
    for kode in daftarKode:
        produk = cariData(fileProduk, 'kode', kode)
        if produk is not None:
            baris.append([produk['kode'], produk['nama'], produk['warna'], produk['ukuran'],
                          formatRupiah(produk['harga'])])
    tampilkanTabel(['Kode', 'Nama', 'Warna', 'Ukuran', 'Harga/Hari'], baris, ('Harga/Hari',))


def pilihPaket():
    # Mengembalikan dict paket terpilih (berisi daftar kode barang), atau None
    cetakJudul('PAKET ACARA')
    show_packages()
    kode = input('\nMasukkan kode paket (0 = kembali): ').strip().upper()
    if kode == '0':
        return None
    paket = cariData(filePaket, 'kode', kode)
    if paket is None or not paket['aktif']:
        pesanGagal('Kode paket tidak valid atau paket nonaktif!')
        return None

    kodeItems = []
    for slot in paket['komposisi']:
        if len(slot['pilihan']) == 1:
            kodeBarang = slot['pilihan'][0]
        else:
            print(f'\nPilih {slot["label"]}:')
            tampilkanOpsi(slot['pilihan'])
            while True:
                kodeBarang = input('Kode pilihan (0 = batal): ').strip().upper()
                if kodeBarang == '0':
                    return None
                if kodeBarang in slot['pilihan']:
                    break
                pesanGagal('Pilihan tidak valid untuk paket ini!')
        produk = cariData(fileProduk, 'kode', kodeBarang)
        if produk is None or not produk['aktif']:
            pesanGagal(f'Barang {kodeBarang} tidak ditemukan atau nonaktif. Paket tidak dapat dipesan!')
            return None
        kodeItems.append(kodeBarang)
    return {'kode': paket['kode'], 'nama': paket['nama'], 'mua': paket['mua'],
            'kodeItems': kodeItems}


# ---------- CRUD PAKET ----------

def inputKomposisi():
    # mengembalikan list slot komposisi, atau None jika batal
    komposisi = []
    while True:
        label = inputTeks('Nama barang dalam paket (0 = selesai): ')
        if label == '0':
            break
        teks = inputTeks('Kode produk pilihan (pisahkan dengan koma, contoh KB-PNK-S,KB-PNK-M): ')
        pilihan = []
        for kode in teks.upper().split(','):
            kode = kode.strip()
            if cariData(fileProduk, 'kode', kode) is None:
                pesanGagal(f'Kode produk {kode} tidak ditemukan!')
                pilihan = []
                break
            pilihan.append(kode)
        if len(pilihan) == 0:
            continue
        if len(set(pilihan)) != len(pilihan):
            pesanGagal('Ada kode produk yang ganda!')
            continue
        komposisi.append({'label': label, 'pilihan': pilihan})
        pesanBerhasil('Barang ditambahkan ke komposisi.')
    if len(komposisi) == 0:
        pesanGagal('Komposisi paket tidak boleh kosong!')
        return None
    return komposisi


def inputKodeMUA():
    show_mua_services_singkat()
    while True:
        kode = input('Kode kategori MUA paket (kosong = tanpa MUA): ').strip().upper()
        if kode == '' or cariData(fileMUA, 'kode', kode) is not None:
            return kode
        pesanGagal('Kode kategori MUA tidak ditemukan!')


def show_mua_services_singkat():
    baris = []
    for layanan in bacaJSON(fileMUA):
        baris.append([layanan['kode'], layanan['nama'], formatRupiah(layanan['harga'])])
    tampilkanTabel(['Kode', 'Kategori', 'Harga/Sesi'], baris, ('Harga/Sesi',))


def add_package():
    cetakJudul('TAMBAH PAKET ACARA')
    kode = generateKode('PKA', bacaJSON(filePaket), 'kode')
    print(f'Kode paket otomatis: {kode}')
    nama = inputTeks('Nama paket (0 = batal): ')
    if nama == '0':
        return
    kodeMUA = inputKodeMUA()
    komposisi = inputKomposisi()
    if komposisi is None:
        return
    tambahData(filePaket, {'kode': kode, 'nama': nama, 'mua': kodeMUA,
                           'aktif': True, 'komposisi': komposisi})
    pesanBerhasil('Paket berhasil ditambahkan.')


def update_package():
    cetakJudul('UBAH PAKET ACARA')
    show_packages()
    kode = inputTeks('Kode paket (0 = batal): ').upper()
    if kode == '0':
        return
    paket = cariData(filePaket, 'kode', kode)
    if paket is None:
        pesanGagal('Kode paket tidak ditemukan!')
        return
    print('Kosongkan input jika tidak ingin mengubah.')
    nama = input(f'Nama paket ({paket["nama"]}): ').strip()
    if nama != '':
        paket['nama'] = nama
    if inputYaTidak('Ubah kategori MUA? (y/n): '):
        paket['mua'] = inputKodeMUA()
    if inputYaTidak('Ganti seluruh komposisi barang? (y/n): '):
        komposisi = inputKomposisi()
        if komposisi is None:
            return
        paket['komposisi'] = komposisi
    if inputYaTidak('Ubah status aktif/nonaktif? (y/n): '):
        paket['aktif'] = not paket['aktif']
    ubahData(filePaket, 'kode', kode, paket)
    pesanBerhasil('Paket berhasil diubah.')


def delete_package():
    cetakJudul('HAPUS PAKET ACARA')
    show_packages()
    kode = inputTeks('Kode paket (0 = batal): ').upper()
    if kode == '0':
        return
    if cariData(filePaket, 'kode', kode) is None:
        pesanGagal('Kode paket tidak ditemukan!')
        return
    for rental in bacaJSON(fileRental):
        if rental['paket'] is not None and rental['paket']['kode'] == kode:
            if rental['statusRental'] in statusAktif:
                pesanGagal(f'Paket masih dipakai transaksi aktif {rental["kode"]}!')
                return
    if inputYaTidak('Yakin hapus paket ini? (y/n): '):
        hapusData(filePaket, 'kode', kode)
        pesanBerhasil('Paket berhasil dihapus.')
    else:
        pesanInfo('Penghapusan dibatalkan.')


def manage_packages(user):
    if not cekAkses(user, ('Admin',)):
        return
    while True:
        cetakJudul('KELOLA PAKET ACARA')
        cetakMenu(['1. Tambah', '2. Ubah', '3. Hapus', '4. Lihat', '0. Kembali'])
        pilihan = inputPilihanMenu('Pilih menu: ', ('1', '2', '3', '4', '0'))
        if pilihan == '0':
            return
        elif pilihan == '1':
            add_package()
        elif pilihan == '2':
            update_package()
        elif pilihan == '3':
            delete_package()
        else:
            cetakJudul('DAFTAR PAKET ACARA')
            show_packages()
        tungguEnter()
