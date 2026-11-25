from utils.database import (bacaJSON, tambahData, cariData, ubahData,
                            fileRental, filePembayaran)
from utils.helpers import (formatRupiah, generateKode, waktuSekarangTeks, hitungStatusBayar,
                           namaStatusRental, namaStatusBayar)
from utils.display import (cetakJudul, cetakMenu, pesanBerhasil, pesanGagal,
                           pesanInfo, tampilkanTabel, tungguEnter)
from utils.validation import (inputAngka, inputYaTidak, inputPilihanMenu)


def hitungTotalDibayar(kodeRental):
    # hanya pembayaran yang sudah dikonfirmasi
    total = 0
    for pembayaran in bacaJSON(filePembayaran):
        if pembayaran['kodeRental'] == kodeRental and pembayaran['dikonfirmasi']:
            total += pembayaran['nominal']
    return total


def hitungTertunda(kodeRental):
    total = 0
    for pembayaran in bacaJSON(filePembayaran):
        if pembayaran['kodeRental'] == kodeRental and not pembayaran['dikonfirmasi']:
            total += pembayaran['nominal']
    return total



def daftarTertunda(kodeRental):
    hasil = []
    for pembayaran in bacaJSON(filePembayaran):
        if pembayaran['kodeRental'] == kodeRental and not pembayaran['dikonfirmasi']:
            hasil.append(pembayaran)
    return hasil

def tampilkanTagihan(rental):
    dibayar = hitungTotalDibayar(rental['kode'])
    sisa = rental['totalAkhir'] - dibayar
    print(f'Kode rental      : {rental["kode"]}')
    print(f'Pelanggan        : {rental["namaPelanggan"]} ({rental["idPelanggan"]})')
    print(f'Status rental    : {rental["statusRental"]} - {namaStatusRental[rental["statusRental"]]}')
    print(f'Total awal       : {formatRupiah(rental["totalAwal"])}')
    print(f'Denda            : {formatRupiah(rental["denda"])}')
    print(f'Total tagihan    : {formatRupiah(rental["totalAkhir"])}')
    print(f'Minimal DP (30%) : {formatRupiah(rental["minimalDP"])}')
    print(f'Sudah dibayar    : {formatRupiah(dibayar)} (terkonfirmasi)')
    print(f'Sisa tagihan     : {formatRupiah(sisa)}')
    return sisa


def cetakBukti(pembayaran, rental):
    cetakJudul('BUKTI PEMBAYARAN')
    print(f'Kode pembayaran  : {pembayaran["kode"]}')
    print(f'Kode rental      : {rental["kode"]}')
    print(f'Tanggal          : {pembayaran["tanggal"]}')
    print(f'Nominal          : {formatRupiah(pembayaran["nominal"])}')
    print(f'Dikonfirmasi oleh: {pembayaran["dikonfirmasiOleh"]}')
    print(f'Total dibayar    : {formatRupiah(rental["totalDibayar"])}')
    print(f'Sisa tagihan     : {formatRupiah(rental["totalAkhir"] - rental["totalDibayar"])}')
    print(f'Status pembayaran: {rental["statusBayar"]} - {namaStatusBayar[rental["statusBayar"]]}')
    print(f'Status rental    : {rental["statusRental"]} - {namaStatusRental[rental["statusRental"]]}')


def confirm_payment(user, pembayaran):
    # hanya Admin atau Petugas yang boleh memanggil fungsi ini
    pembayaran['dikonfirmasi'] = True
    pembayaran['dikonfirmasiOleh'] = user['nama']
    pembayaran['tanggalKonfirmasi'] = waktuSekarangTeks()
    ubahData(filePembayaran, 'kode', pembayaran['kode'], pembayaran)

    rental = cariData(fileRental, 'kode', pembayaran['kodeRental'])
    rental['totalDibayar'] = hitungTotalDibayar(rental['kode'])
    rental['statusBayar'] = hitungStatusBayar(rental['totalDibayar'], rental['totalAkhir'])
    # DP minimal terpenuhi -> siap diambil
    if rental['statusRental'] == 'ST-01' and rental['totalDibayar'] >= rental['minimalDP']:
        rental['statusRental'] = 'ST-02'
    ubahData(fileRental, 'kode', rental['kode'], rental)
    cetakBukti(pembayaran, rental)


def catatPembayaran(user, rental, sisa):
    sisaBisaDibayar = sisa - hitungTertunda(rental['kode'])
    if sisaBisaDibayar <= 0:
        pesanInfo('Seluruh sisa tagihan sudah tercatat dan menunggu konfirmasi.')
        return
    print(f'Nominal maksimal yang dapat dicatat: {formatRupiah(sisaBisaDibayar)}')
    nominal = inputAngka('Nominal pembayaran (0 = batal): ', 0)
    if nominal == 0:
        pesanInfo('Pembayaran dibatalkan.')
        return
    if nominal > sisaBisaDibayar:
        pesanGagal('Pembayaran ditolak! Nominal melebihi sisa tagihan.')
        return

    pembayaran = {
        'kode': generateKode('PAY', bacaJSON(filePembayaran), 'kode'),
        'kodeRental': rental['kode'],
        'nominal': nominal,
        'tanggal': waktuSekarangTeks(),
        'dikonfirmasi': False,
        'dikonfirmasiOleh': '-',
        'tanggalKonfirmasi': '-'
    }
    tambahData(filePembayaran, pembayaran)
    pesanBerhasil(f'Pembayaran {pembayaran["kode"]} sebesar {formatRupiah(nominal)} tercatat.')

    if user['role'] in ('Admin', 'Petugas'):
        if inputYaTidak('Konfirmasi pembayaran ini sekarang? (y/n): '):
            confirm_payment(user, pembayaran)
        else:
            pesanInfo('Pembayaran belum dikonfirmasi.')
    else:
        pesanInfo('Pembayaran belum dikonfirmasi. Serahkan pembayaran ke Petugas/Admin untuk dikonfirmasi.')


def konfirmasiTertunda(user, rental):
    daftar = daftarTertunda(rental['kode'])
    if len(daftar) == 0:
        pesanInfo('Tidak ada pembayaran yang menunggu konfirmasi.')
        return
    baris = []
    for pembayaran in daftar:
        baris.append([pembayaran['kode'], formatRupiah(pembayaran['nominal']), pembayaran['tanggal']])
    tampilkanTabel(['Kode PAY', 'Nominal', 'Tanggal Dicatat'], baris, ('Nominal',))
    kode = input('Kode PAY yang dikonfirmasi (0 = batal): ').strip().upper()
    if kode == '0':
        return
    pembayaran = cariData(filePembayaran, 'kode', kode)
    if pembayaran is None or pembayaran['kodeRental'] != rental['kode'] or pembayaran['dikonfirmasi']:
        pesanGagal('Kode pembayaran tidak valid!')
        return
    confirm_payment(user, pembayaran)


def process_payment(user, kodeAwal=None):
    # Flowchart halaman 14 (N)
    cetakJudul('PEMBAYARAN')
    while True:
        if kodeAwal is None:
            kode = input('Kode rental (0 = kembali): ').strip().upper()
        else:
            kode = kodeAwal
            kodeAwal = None
        if kode == '0':
            return
        rental = cariData(fileRental, 'kode', kode)
        if rental is None:
            pesanGagal('Kode rental tidak valid!')
            continue
        if user['role'] == 'Pelanggan' and rental['idPelanggan'] != user['idPelanggan']:
            pesanGagal('Kode rental tidak valid!')
            continue
        if rental['statusRental'] == 'ST-06':
            pesanGagal('Transaksi sudah dibatalkan. Pembayaran tidak dapat dilakukan.')
            return
        break

    sisa = tampilkanTagihan(rental)
    if sisa <= 0:
        pesanBerhasil('Transaksi ini sudah lunas.')
        return

    if user['role'] == 'Pelanggan':
        catatPembayaran(user, rental, sisa)
        return

    cetakMenu(['1. Catat Pembayaran Baru', '2. Konfirmasi Pembayaran Tertunda', '0. Kembali'])
    pilihan = inputPilihanMenu('Pilih menu: ', ('1', '2', '0'))
    if pilihan == '1':
        catatPembayaran(user, rental, sisa)
    elif pilihan == '2':
        konfirmasiTertunda(user, rental)