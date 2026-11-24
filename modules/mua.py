from utils.database import (bacaJSON, tambahData, cariData, ubahData, hapusData, simpanJSON,
                            fileMUA, fileRental)
from utils.helpers import (formatRupiah, ubahTanggal, hariIni, generateKode, statusAktif)
from utils.display import (cetakJudul, cetakMenu, pesanBerhasil, pesanGagal,
                           pesanInfo, tampilkanTabel, tungguEnter)
from utils.validation import (inputTeks, inputAngka, inputYaTidak, inputTanggal,
                              inputPilihanMenu, cekAkses)

daftarSesiAwal = ['Pagi', 'Siang', 'Sore', 'Malam']


def show_mua_services():
    baris = []
    for layanan in bacaJSON(fileMUA):
        baris.append([layanan['kode'], layanan['nama'], formatRupiah(layanan['harga']),
                      ', '.join(layanan['sesi']), len(layanan['jadwal'])])
    tampilkanTabel(['Kode', 'Kategori Acara', 'Harga/Sesi', 'Sesi', 'Booking'],
                   baris, ('Harga/Sesi', 'Booking'))


def show_mua_schedule():
    baris = []
    for layanan in bacaJSON(fileMUA):
        for jadwal in layanan['jadwal']:
            baris.append([jadwal['kode'], layanan['nama'], jadwal['tanggal'],
                          jadwal['sesi'], jadwal['kodeRental']])
    tampilkanTabel(['Kode MUA', 'Kategori', 'Tanggal', 'Sesi', 'Kode Rental'], baris)


def sesiTersedia(layanan, tanggal, sesi):
    for jadwal in layanan['jadwal']:
        if jadwal['tanggal'] == tanggal and jadwal['sesi'] == sesi:
            return False
    return True


def pilihMUA(kodeKategoriTetap=None):
    # Mengembalikan data booking MUA (dict), atau None jika tidak jadi memakai MUA
    cetakJudul('LAYANAN MUA')
    if kodeKategoriTetap is None:
        show_mua_services()
        kode = input('Kode kategori MUA (0 = batal): ').strip().upper()
        if kode == '0':
            return None
    else:
        kode = kodeKategoriTetap
    layanan = cariData(fileMUA, 'kode', kode)
    if layanan is None:
        pesanGagal('Kategori layanan MUA tidak ditemukan!')
        return None
    print(f'Layanan : MUA {layanan["nama"]} ({layanan["kode"]})')
    print(f'Harga   : {formatRupiah(layanan["harga"])} per sesi')

    while True:
        tanggal = inputTanggal('Tanggal MUA DD-MM-YYYY (0 = batal): ', True)
        if tanggal == '0':
            return None
        if ubahTanggal(tanggal) < hariIni():
            pesanGagal('Tanggal booking MUA tidak boleh di masa lalu!')
            continue

        print('Sesi tersedia pada tanggal tersebut:')
        for nomor in range(len(layanan['sesi'])):
            sesi = layanan['sesi'][nomor]
            if sesiTersedia(layanan, tanggal, sesi):
                print(f'  {nomor + 1}. {sesi}')
            else:
                print(f'  {nomor + 1}. {sesi} (sudah terisi)')
        pilihan = input('Pilih nomor sesi (0 = ganti tanggal): ').strip()
        if pilihan == '0':
            continue
        if not pilihan.isdigit() or int(pilihan) < 1 or int(pilihan) > len(layanan['sesi']):
            pesanGagal('Pilihan sesi tidak valid!')
            continue
        sesiDipilih = layanan['sesi'][int(pilihan) - 1]
        if not sesiTersedia(layanan, tanggal, sesiDipilih):
            pesanGagal('Sesi sudah terisi. Silakan pilih sesi lain.')
            continue
        return {'kodeLayanan': layanan['kode'], 'kategori': layanan['nama'],
                'tanggal': tanggal, 'sesi': sesiDipilih, 'harga': layanan['harga']}


def tahanJadwalMUA(booking, kodeRental):
    # menyimpan jadwal MUA dan mengembalikan kode MUA otomatis
    dataMUA = bacaJSON(fileMUA)
    semuaJadwal = []
    for layanan in dataMUA:
        for jadwal in layanan['jadwal']:
            semuaJadwal.append(jadwal)
    kodeMUA = generateKode('MUA', semuaJadwal, 'kode')

    for layanan in dataMUA:
        if layanan['kode'] == booking['kodeLayanan']:
            if not sesiTersedia(layanan, booking['tanggal'], booking['sesi']):
                return None
            layanan['jadwal'].append({'kode': kodeMUA, 'tanggal': booking['tanggal'],
                                      'sesi': booking['sesi'], 'kodeRental': kodeRental})
    simpanJSON(fileMUA, dataMUA)
    return kodeMUA


def lepasJadwalMUA(kodeRental):
    dataMUA = bacaJSON(fileMUA)
    for layanan in dataMUA:
        jadwalBaru = []
        for jadwal in layanan['jadwal']:
            if jadwal['kodeRental'] != kodeRental:
                jadwalBaru.append(jadwal)
        layanan['jadwal'] = jadwalBaru
    simpanJSON(fileMUA, dataMUA)


# ---------- CRUD MUA ----------

def add_mua():
    cetakJudul('TAMBAH LAYANAN MUA')
    kode = inputTeks('Kode layanan (contoh CAT-M05, 0 = batal): ').upper()
    if kode == '0':
        return
    if cariData(fileMUA, 'kode', kode) is not None:
        pesanGagal('Kode layanan sudah digunakan!')
        return
    nama = inputTeks('Kategori acara: ')
    harga = inputAngka('Harga per sesi: ', 1)
    tambahData(fileMUA, {'kode': kode, 'nama': nama, 'harga': harga,
                         'sesi': list(daftarSesiAwal), 'jadwal': []})
    pesanBerhasil('Layanan MUA berhasil ditambahkan dengan 4 sesi.')


def update_mua():
    cetakJudul('UBAH LAYANAN MUA')
    show_mua_services()
    kode = inputTeks('Kode layanan (0 = batal): ').upper()
    if kode == '0':
        return
    layanan = cariData(fileMUA, 'kode', kode)
    if layanan is None:
        pesanGagal('Kode layanan tidak ditemukan!')
        return
    print('Kosongkan input jika tidak ingin mengubah.')
    nama = input(f'Kategori acara ({layanan["nama"]}): ').strip()
    harga = input(f'Harga per sesi ({layanan["harga"]}): ').strip()
    if nama != '':
        layanan['nama'] = nama
    if harga != '':
        if harga.isdigit() and int(harga) > 0:
            layanan['harga'] = int(harga)
        else:
            pesanGagal('Harga harus berupa angka lebih dari 0!')
            return
    ubahData(fileMUA, 'kode', kode, layanan)
    pesanBerhasil('Layanan MUA berhasil diubah. Booking lama tetap memakai harga lamanya.')


def delete_mua():
    cetakJudul('HAPUS LAYANAN MUA')
    show_mua_services()
    kode = inputTeks('Kode layanan (0 = batal): ').upper()
    if kode == '0':
        return
    layanan = cariData(fileMUA, 'kode', kode)
    if layanan is None:
        pesanGagal('Kode layanan tidak ditemukan!')
        return
    for rental in bacaJSON(fileRental):
        if rental['mua'] is not None and rental['mua']['kodeLayanan'] == kode:
            if rental['statusRental'] in statusAktif:
                pesanGagal(f'Layanan masih terikat booking aktif di {rental["kode"]}!')
                return
    if inputYaTidak('Yakin hapus layanan ini? (y/n): '):
        hapusData(fileMUA, 'kode', kode)
        pesanBerhasil('Layanan MUA berhasil dihapus.')
    else:
        pesanInfo('Penghapusan dibatalkan.')


def manage_mua(user):
    if not cekAkses(user, ('Admin',)):
        return
    while True:
        cetakJudul('KELOLA LAYANAN MUA')
        cetakMenu(['1. Tambah', '2. Ubah', '3. Hapus', '4. Lihat Layanan dan Jadwal', '0. Kembali'])
        pilihan = inputPilihanMenu('Pilih menu: ', ('1', '2', '3', '4', '0'))
        if pilihan == '0':
            return
        elif pilihan == '1':
            add_mua()
        elif pilihan == '2':
            update_mua()
        elif pilihan == '3':
            delete_mua()
        else:
            cetakJudul('LAYANAN MUA')
            show_mua_services()
            print('\nJadwal booking:')
            show_mua_schedule()
        tungguEnter()
