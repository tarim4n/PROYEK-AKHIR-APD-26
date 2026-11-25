from utils.database import bacaJSON, fileRental, fileProduk, fileKategori, filePembayaran
from utils.helpers import formatRupiah, tanggalKeTeks, hariIni, namaStatusRental
from utils.display import (cetakJudul, cetakMenu, pesanGagal, pesanInfo,
                           tampilkanTabel, tungguEnter)
from utils.validation import inputPilihanMenu, cekAkses
from modules.catalog import hitungTersedia, hitungJumlahStatus
from modules.rental import tampilkanDaftarRental, tampilkanDetailRental


def hitungPendapatan():
    total = 0
    for pembayaran in bacaJSON(filePembayaran):
        if pembayaran['dikonfirmasi']:
            total += pembayaran['nominal']
    return total


def hitungTotalDenda():
    total = 0
    for rental in bacaJSON(fileRental):
        total += rental['denda']
    return total


def hitungPerStatus():
    hasil = {}
    for kode in namaStatusRental:
        hasil[kode] = 0
    for rental in bacaJSON(fileRental):
        hasil[rental['statusRental']] += 1
    return hasil


def show_transaction_report(user):
    cetakJudul('LAPORAN TRANSAKSI')
    dataRental = bacaJSON(fileRental)
    if len(dataRental) == 0:
        pesanInfo('Belum ada transaksi.')
        return
    tampilkanDaftarRental(dataRental)

    print('\nJumlah transaksi berdasarkan status:')
    baris = []
    perStatus = hitungPerStatus()
    for kode in perStatus:
        baris.append([kode, namaStatusRental[kode], perStatus[kode]])
    baris.append(['', 'TOTAL', len(dataRental)])
    tampilkanTabel(['Kode', 'Status', 'Jumlah'], baris, ('Jumlah',))

    while True:
        kode = input('\nKode transaksi untuk detail (0 = kembali): ').strip().upper()
        if kode == '0':
            return
        for rental in dataRental:
            if rental['kode'] == kode:
                tampilkanDetailRental(rental)
                return
        pesanGagal('Kode transaksi tidak valid!')


def show_income_report():
    cetakJudul('LAPORAN PENDAPATAN DAN DENDA')
    baris = []
    for pembayaran in bacaJSON(filePembayaran):
        if pembayaran['dikonfirmasi']:
            status = 'Dikonfirmasi'
        else:
            status = 'Belum dikonfirmasi (tidak dihitung)'
        baris.append([pembayaran['kode'], pembayaran['kodeRental'], formatRupiah(pembayaran['nominal']),
                      pembayaran['tanggal'], status])
    tampilkanTabel(['Kode PAY', 'Kode Rental', 'Nominal', 'Tanggal', 'Status'], baris, ('Nominal',))
    print(f'\nTotal pembayaran terkonfirmasi : {formatRupiah(hitungPendapatan())}')
    print(f'Total denda                    : {formatRupiah(hitungTotalDenda())}')


def show_stock_report():
    cetakJudul('LAPORAN STOK')
    hari = tanggalKeTeks(hariIni())
    baris = []
    totalStok = 0
    for produk in bacaJSON(fileProduk):
        disewa = hitungJumlahStatus(produk['kode'], ('ST-03', 'ST-04'))
        dipesan = hitungJumlahStatus(produk['kode'], ('ST-01', 'ST-02'))
        tersedia = hitungTersedia(produk['kode'], hari, hari)
        totalStok += produk['stok']
        nama = produk['nama']
        if produk['jenis'] != '':
            nama = nama + ' (' + produk['jenis'] + ')'
        baris.append([produk['kode'], nama, produk['stok'], disewa, dipesan, tersedia])
    tampilkanTabel(['Kode', 'Nama', 'Stok', 'Disewa', 'Dipesan', 'Sedia Hari Ini'],
                   baris, ('Stok', 'Disewa', 'Dipesan', 'Sedia Hari Ini'))
    print(f'\nTotal {len(baris)} variasi, total stok fisik {totalStok} unit.')
    print('Disewa = transaksi Sedang Disewa + Terlambat.')
    print('Dipesan = transaksi Menunggu Pembayaran + Menunggu Pengambilan (menahan stok sesuai periode).')


def ambilPyplot():
    try:
        import matplotlib.pyplot as plt
        return plt
    except ImportError:
        pesanGagal('Matplotlib belum terpasang. Jalankan: python3 -m pip install matplotlib')
        return None


def grafikStatus(plt):
    perStatus = hitungPerStatus()
    if sum(perStatus.values()) == 0:
        pesanInfo('Data grafik belum tersedia karena belum ada transaksi.')
        return
    label = list(perStatus.keys())
    nilai = list(perStatus.values())
    plt.figure(figsize=(8, 5))
    plt.bar(label, nilai, color='tab:purple')
    plt.title('Jumlah Transaksi Berdasarkan Status')
    plt.xlabel('Status Rental')
    plt.ylabel('Jumlah Transaksi')
    plt.show()



def grafikKategori(plt):
    dataProduk = bacaJSON(fileProduk)
    label = []
    nilai = []
    for kategori in bacaJSON(fileKategori):
        jumlah = 0
        for produk in dataProduk:
            if produk['kategori'] == kategori['kode']:
                jumlah += 1
        label.append(kategori['nama'])
        nilai.append(jumlah)
    if sum(nilai) == 0:
        pesanInfo('Data grafik belum tersedia.')
        return
    plt.figure(figsize=(9, 5))
    plt.bar(label, nilai, color='tab:blue')
    plt.title('Jumlah Variasi Produk Berdasarkan Kategori')
    plt.xticks(rotation=30)
    plt.ylabel('Jumlah Variasi')
    plt.tight_layout()
    plt.show()


def grafikPendapatan(plt):
    pendapatan = hitungPendapatan()
    denda = hitungTotalDenda()
    if pendapatan == 0 and denda == 0:
        pesanInfo('Data grafik belum tersedia karena belum ada pembayaran atau denda.')
        return
    plt.figure(figsize=(6, 5))
    plt.bar(['Pembayaran Terkonfirmasi', 'Denda'], [pendapatan, denda], color=['tab:green', 'tab:red'])
    plt.title('Pendapatan dan Denda (Rp)')
    plt.ylabel('Rupiah')
    plt.show()

def grafikStok(plt):
    dataProduk = bacaJSON(fileProduk)
    label = []
    stok = []
    disewa = []
    for kategori in bacaJSON(fileKategori):
        jumlahStok = 0
        jumlahDisewa = 0
        for produk in dataProduk:
            if produk['kategori'] == kategori['kode']:
                jumlahStok += produk['stok']
                jumlahDisewa += hitungJumlahStatus(produk['kode'], ('ST-03', 'ST-04'))
        label.append(kategori['nama'])
        stok.append(jumlahStok)
        disewa.append(jumlahDisewa)
    if sum(stok) == 0:
        pesanInfo('Data grafik belum tersedia.')
        return
    posisi = list(range(len(label)))
    geser = []
    for nomor in posisi:
        geser.append(nomor + 0.4)
    plt.figure(figsize=(9, 5))
    plt.bar(posisi, stok, width=0.4, label='Stok fisik', color='tab:blue')
    plt.bar(geser, disewa, width=0.4, label='Sedang disewa', color='tab:orange')
    plt.xticks(geser, label, rotation=30)
    plt.title('Stok Produk per Kategori')
    plt.legend()
    plt.tight_layout()
    plt.show()


def show_statistics():
    plt = ambilPyplot()
    if plt is None:
        return
    while True:
        cetakJudul('STATISTIK DAN GRAFIK')
        cetakMenu(['1. Transaksi Berdasarkan Status', '2. Produk Berdasarkan Kategori',
                   '3. Pendapatan dan Denda', '4. Stok per Kategori', '0. Kembali'])
        pilihan = inputPilihanMenu('Pilih grafik: ', ('1', '2', '3', '4', '0'))
        if pilihan == '0':
            return
        elif pilihan == '1':
            grafikStatus(plt)
        elif pilihan == '2':
            grafikKategori(plt)
        elif pilihan == '3':
            grafikPendapatan(plt)
        else:
            grafikStok(plt)
        tungguEnter()



def menu_reports(user):
    if not cekAkses(user, ('Admin', 'Petugas')):
        return
    while True:
        cetakJudul('LAPORAN DAN STATISTIK')
        cetakMenu(['1. Laporan Transaksi', '2. Laporan Pendapatan dan Denda',
                   '3. Laporan Stok', '4. Statistik dan Grafik', '0. Kembali'])
        pilihan = inputPilihanMenu('Pilih menu: ', ('1', '2', '3', '4', '0'))
        if pilihan == '0':
            return
        elif pilihan == '1':
            show_transaction_report(user)
        elif pilihan == '3':
            show_stock_report()
        elif user['role'] != 'Admin':
            pesanGagal('Akses terbatas! Menu ini hanya untuk Admin.')
        elif pilihan == '2':
            show_income_report()
        else:
            show_statistics()
            continue
        tungguEnter()