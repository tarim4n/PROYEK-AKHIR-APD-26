from utils.database import bacaJSON, cariData, ubahData, simpanJSON, fileRental
from utils.helpers import (formatRupiah, ubahTanggal, hariIni, hitungStatusBayar,
                           namaStatusRental, namaStatusBayar)
from utils.display import (cetakJudul, pesanBerhasil, pesanGagal, pesanInfo)
from utils.validation import inputYaTidak, inputTanggal, cekAkses


def check_late_status():
    # BR-34: status ST-03 menjadi ST-04 jika tanggal akhir sudah lewat (tanggal komputer)
    dataRental = bacaJSON(fileRental)
    jumlah = 0
    for rental in dataRental:
        if rental['statusRental'] == 'ST-03':
            if hariIni() > ubahTanggal(rental['tanggalAkhir']):
                rental['statusRental'] = 'ST-04'
                jumlah += 1
    if jumlah > 0:
        simpanJSON(fileRental, dataRental)
        pesanInfo(f'{jumlah} transaksi berstatus Terlambat (ST-04).')
    return jumlah



def hitungDenda(subtotalRental, hariTerlambat):
    # denda = 20% x subtotal rental x hari terlambat (tanpa biaya MUA)
    return subtotalRental * 20 * hariTerlambat // 100

def process_return(user):
    # Flowchart halaman 16 (P)
    if not cekAkses(user, ('Admin', 'Petugas')):
        return
    cetakJudul('PENGEMBALIAN DAN DENDA')
    while True:
        kode = input('Kode rental (0 = kembali): ').strip().upper()
        if kode == '0':
            return
        rental = cariData(fileRental, 'kode', kode)
        if rental is None:
            pesanGagal('Kode rental tidak valid!')
        else:
            break

    if rental['statusRental'] not in ('ST-03', 'ST-04'):
        pesanGagal(f'Pengembalian ditolak! Status saat ini {rental["statusRental"]} - {namaStatusRental[rental["statusRental"]]}.')
        return

    print(f'Pelanggan     : {rental["namaPelanggan"]}')
    print(f'Periode sewa  : {rental["tanggalMulai"]} s.d. {rental["tanggalAkhir"]}')

    while True:
        tanggalAktual = inputTanggal('Tanggal pengembalian aktual DD-MM-YYYY (0 = batal): ', True)
        if tanggalAktual == '0':
            return
        if ubahTanggal(tanggalAktual) < ubahTanggal(rental['tanggalMulai']):
            pesanGagal('Tanggal pengembalian tidak boleh sebelum tanggal mulai!')
        elif ubahTanggal(tanggalAktual) > hariIni():
            pesanGagal('Tanggal pengembalian tidak boleh di masa depan!')
        else:
            break

    hariTerlambat = (ubahTanggal(tanggalAktual) - ubahTanggal(rental['tanggalAkhir'])).days
    if hariTerlambat > 0:
        denda = hitungDenda(rental['subtotalRental'], hariTerlambat)
        if rental['statusRental'] == 'ST-03':
            rental['statusRental'] = 'ST-04'
            ubahData(fileRental, 'kode', kode, rental)
        pesanInfo(f'Terlambat {hariTerlambat} hari. Denda = 20% x subtotal rental x {hariTerlambat} hari.')
    else:
        hariTerlambat = 0
        denda = 0
        pesanInfo('Pengembalian tidak terlambat. Denda Rp0.')

    totalAkhir = rental['totalAwal'] + denda
    sisa = totalAkhir - rental['totalDibayar']
    print(f'Denda         : {formatRupiah(denda)}')
    print(f'Total akhir   : {formatRupiah(totalAkhir)}')
    print(f'Total dibayar : {formatRupiah(rental["totalDibayar"])}')
    print(f'Sisa tagihan  : {formatRupiah(sisa)}')

    if not inputYaTidak('\nKondisi barang baik? (y/n): '):
        pesanGagal('Pengembalian belum dapat diselesaikan. Penanganan barang rusak/hilang di luar ruang lingkup versi pertama.')
        return
    if not inputYaTidak('Konfirmasi pengembalian? (y/n): '):
        pesanInfo('Pengembalian belum dikonfirmasi.')
        return

    rental['pengembalian'] = {'tanggalAktual': tanggalAktual, 'hariTerlambat': hariTerlambat,
                              'kondisi': 'Baik', 'petugas': user['nama']}
    rental['denda'] = denda
    rental['totalAkhir'] = totalAkhir
    rental['statusRental'] = 'ST-05'
    rental['statusBayar'] = hitungStatusBayar(rental['totalDibayar'], totalAkhir)
    ubahData(fileRental, 'kode', kode, rental)

    pesanBerhasil('\nPengembalian dikonfirmasi. Status menjadi ST-05 Selesai. Barang tersedia kembali.')
    print(f'Hari terlambat    : {hariTerlambat}')
    print(f'Denda             : {formatRupiah(denda)}')
    print(f'Total akhir       : {formatRupiah(totalAkhir)}')
    print(f'Total dibayar     : {formatRupiah(rental["totalDibayar"])}')
    print(f'Sisa tagihan      : {formatRupiah(sisa)}')
    print(f'Status pembayaran : {rental["statusBayar"]} - {namaStatusBayar[rental["statusBayar"]]}')
    if sisa > 0:
        pesanInfo('Masih ada sisa tagihan. Pelunasan dilakukan lewat menu Konfirmasi Pembayaran.')
    