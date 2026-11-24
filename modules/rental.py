from datetime import datetime
from utils.database import (bacaJSON, tambahData, cariData, ubahData, simpanJSON,
                            fileRental, fileProduk, filePelanggan, filePembayaran)
from utils.helpers import (formatRupiah, generateKode, ubahTanggal, ubahWaktu, tanggalKeTeks,
                           hariIni, waktuSekarangTeks, batasBayarTeks, hitungDurasi,
                           hitungMinimalDP, namaStatusRental, namaStatusBayar)
from utils.display import (cetakJudul, cetakMenu, pesanBerhasil, pesanGagal,
                           pesanInfo, tampilkanTabel, tungguEnter)
from utils.validation import (inputAngka, inputYaTidak, inputTanggal,
                              inputPilihanMenu, cekAkses)
from modules.catalog import hitungTersedia, tampilkanSemuaProduk
from modules.packages import pilihPaket
from modules.mua import pilihMUA, tahanJadwalMUA, lepasJadwalMUA
from modules.payment import process_payment


# ---------- BANTUAN TAMPILAN ----------

def tampilkanDaftarRental(daftar):
    baris = []
    for rental in daftar:
        baris.append([rental['kode'], rental['namaPelanggan'], rental['tanggalMulai'],
                      rental['tanggalAkhir'], formatRupiah(rental['totalAkhir']),
                      rental['statusRental'] + ' ' + namaStatusRental[rental['statusRental']],
                      rental['statusBayar']])
    tampilkanTabel(['Kode', 'Pelanggan', 'Mulai', 'Kembali', 'Total', 'Status Rental', 'Bayar'],
                   baris, ('Total',))


def tampilkanDetailRental(rental):
    dibayar = rental['totalDibayar']
    cetakJudul(f'DETAIL TRANSAKSI {rental["kode"]}')
    print(f'Pelanggan        : {rental["namaPelanggan"]} ({rental["idPelanggan"]})')
    print(f'Dibuat pada      : {rental["dibuatPada"]}')
    if rental['paket'] is not None:
        print(f'Paket            : {rental["paket"]["nama"]} ({rental["paket"]["kode"]})')
    print('Barang:')
    for item in rental['items']:
        print(f'  - {item["kodeProduk"]} {item["nama"]} x{item["jumlah"]} @ {formatRupiah(item["hargaSewa"])}/hari')
    print(f'Tanggal rental   : {rental["tanggalMulai"]} s.d. {rental["tanggalAkhir"]}')
    print(f'Durasi           : {rental["durasi"]} hari')
    if rental['mua'] is not None:
        mua = rental['mua']
        print(f'MUA              : {mua["kodeMUA"]} {mua["kategori"]}, {mua["tanggal"]} sesi {mua["sesi"]}, {formatRupiah(mua["harga"])}')
    else:
        print('MUA              : tidak memakai')
    print(f'Subtotal rental  : {formatRupiah(rental["subtotalRental"])}')
    print(f'Biaya MUA        : {formatRupiah(rental["biayaMUA"])}')
    print(f'Total awal       : {formatRupiah(rental["totalAwal"])}')
    print(f'Denda            : {formatRupiah(rental["denda"])}')
    print(f'Total akhir      : {formatRupiah(rental["totalAkhir"])}')
    print(f'Total dibayar    : {formatRupiah(dibayar)}')
    print(f'Sisa tagihan     : {formatRupiah(rental["totalAkhir"] - dibayar)}')
    print(f'Status rental    : {rental["statusRental"]} - {namaStatusRental[rental["statusRental"]]}')
    print(f'Status pembayaran: {rental["statusBayar"]} - {namaStatusBayar[rental["statusBayar"]]}')
    if rental['statusRental'] == 'ST-01':
        print(f'Batas bayar DP   : {rental["batasBayar"]}')
    if rental['pengajuanBatal'] and rental['statusRental'] != 'ST-06':
        print('Pengajuan batal  : menunggu konfirmasi Petugas/Admin')
    if rental['pengambilan'] is not None:
        print(f'Pengambilan      : {rental["pengambilan"]["waktu"]} oleh {rental["pengambilan"]["petugas"]}')
    if rental['pengembalian'] is not None:
        kembali = rental['pengembalian']
        print(f'Pengembalian     : {kembali["tanggalAktual"]}, terlambat {kembali["hariTerlambat"]} hari')
    if rental['pembatalan'] is not None:
        batal = rental['pembatalan']
        print(f'Pembatalan       : {batal["waktu"]} ({batal["jenis"]}), refund {formatRupiah(batal["refund"])}')

    baris = []
    for pembayaran in bacaJSON(filePembayaran):
        if pembayaran['kodeRental'] == rental['kode']:
            if pembayaran['dikonfirmasi']:
                status = 'Dikonfirmasi'
            else:
                status = 'Belum dikonfirmasi'
            baris.append([pembayaran['kode'], formatRupiah(pembayaran['nominal']),
                          pembayaran['tanggal'], status])
    if len(baris) > 0:
        print('\nRiwayat pembayaran:')
        tampilkanTabel(['Kode PAY', 'Nominal', 'Tanggal', 'Status'], baris, ('Nominal',))


# ---------- BUAT RENTAL (L dan M) ----------

def pilihPelanggan(user):
    if user['role'] == 'Pelanggan':
        return cariData(filePelanggan, 'id', user['idPelanggan'])
    while True:
        idPelanggan = input('ID pelanggan CUS-XXX (0 = batal): ').strip().upper()
        if idPelanggan == '0':
            return None
        pelanggan = cariData(filePelanggan, 'id', idPelanggan)
        if pelanggan is not None:
            print(f'Pelanggan: {pelanggan["nama"]}')
            return pelanggan
        pesanGagal('ID pelanggan tidak ditemukan! Daftarkan pelanggan lewat menu Kelola Pelanggan.')


def buatPesananSatuan():
    items = []
    cetakJudul('KATALOG RENTAL SATUAN')
    tampilkanSemuaProduk()
    while True:
        kode = input('\nKode produk (0 = selesai/kembali): ').strip().upper()
        if kode == '0':
            break
        produk = cariData(fileProduk, 'kode', kode)
        if produk is None:
            pesanGagal('Kode produk tidak ditemukan!')
            continue
        if not produk['aktif']:
            pesanGagal('Produk nonaktif tidak dapat disewa!')
            continue
        if produk['harga'] is None:
            pesanGagal('Harga produk belum dikonfigurasi. Produk belum dapat disewa.')
            continue
        jumlah = inputAngka('Jumlah: ', 1)
        if jumlah > produk['stok']:
            pesanGagal(f'Jumlah melebihi stok fisik ({produk["stok"]})!')
            continue

        sudahAda = False
        for item in items:
            if item['kodeProduk'] == kode:
                item['jumlah'] += jumlah
                sudahAda = True
        if not sudahAda:
            items.append({'kodeProduk': kode, 'nama': produk['nama'], 'jumlah': jumlah,
                          'hargaSewa': produk['harga']})
        pesanBerhasil(f'{produk["nama"]} ({kode}) x{jumlah} ditambahkan ke pesanan.')
        if not inputYaTidak('Tambah barang lain? (y/n): '):
            break
    if len(items) == 0:
        return None
    return items


def create_package_rental():
    paket = pilihPaket()
    if paket is None:
        return None, None
    items = []
    for kodeBarang in paket['kodeItems']:
        produk = cariData(fileProduk, 'kode', kodeBarang)
        if produk['harga'] is None:
            pesanGagal(f'Harga {kodeBarang} belum dikonfigurasi. Paket belum dapat dipesan.')
            return None, None
        items.append({'kodeProduk': kodeBarang, 'nama': produk['nama'], 'jumlah': 1,
                      'hargaSewa': produk['harga']})
    pesanBerhasil(f'Paket {paket["nama"]} ditambahkan ke pesanan.')
    return items, paket


def inputPeriodeRental():
    # mengembalikan (tanggalMulai, tanggalAkhir) atau (None, None) jika batal
    while True:
        mulai = inputTanggal('Tanggal mulai DD-MM-YYYY (0 = batal): ', True)
        if mulai == '0':
            return None, None
        if ubahTanggal(mulai) < hariIni():
            pesanGagal('Tanggal rental yang sudah lewat ditolak!')
            continue
        break
    while True:
        akhir = inputTanggal('Tanggal kembali DD-MM-YYYY (0 = batal): ', True)
        if akhir == '0':
            return None, None
        if ubahTanggal(akhir) < ubahTanggal(mulai):
            pesanGagal('Tanggal kembali tidak boleh sebelum tanggal mulai!')
            continue
        return mulai, akhir


def cekStokPeriode(items, mulai, akhir):
    cukup = True
    for item in items:
        tersedia = hitungTersedia(item['kodeProduk'], mulai, akhir)
        if tersedia < item['jumlah']:
            pesanGagal(f'Stok {item["kodeProduk"]} tidak cukup pada periode ini (tersedia {tersedia}, dipesan {item["jumlah"]}).')
            cukup = False
    return cukup


def create_rental(user):
    # Flowchart halaman 12 (L) dan 13 (M)
    if not cekAkses(user, ('Admin', 'Petugas', 'Pelanggan')):
        return
    cetakJudul('BUAT RENTAL / PAKET ACARA + MUA')
    pelanggan = pilihPelanggan(user)
    if pelanggan is None:
        return

    cetakMenu(['1. Rental Satuan', '2. Paket Acara', '3. Kembali'])
    pilihan = inputPilihanMenu('Pilih jenis pesanan: ', ('1', '2', '3'))
    paket = None
    if pilihan == '3':
        return
    elif pilihan == '1':
        items = buatPesananSatuan()
    else:
        items, paket = create_package_rental()
    if items is None:
        pesanInfo('Pesanan tidak dibuat.')
        return

    # tanggal dan stok
    mulai, akhir = inputPeriodeRental()
    if mulai is None:
        pesanInfo('Pesanan dibatalkan.')
        return
    durasi = hitungDurasi(mulai, akhir)
    if not cekStokPeriode(items, mulai, akhir):
        pesanGagal('Stok tidak mencukupi. Transaksi tidak dapat dilanjutkan.')
        return

    # ringkasan dan MUA
    hargaPerHari = 0
    for item in items:
        hargaPerHari += item['hargaSewa'] * item['jumlah']
    subtotal = hargaPerHari * durasi

    cetakJudul('RINGKASAN PESANAN')
    for item in items:
        print(f'- {item["kodeProduk"]} {item["nama"]} x{item["jumlah"]} @ {formatRupiah(item["hargaSewa"])}/hari')
    print(f'Tanggal : {mulai} s.d. {akhir}')
    print(f'Durasi  : {durasi} hari')

    booking = None
    if inputYaTidak('\nIngin menggunakan layanan MUA? (y/n): '):
        kategoriTetap = None
        if paket is not None and paket['mua'] != '':
            kategoriTetap = paket['mua']
        booking = pilihMUA(kategoriTetap)
        if booking is None:
            pesanInfo('Pesanan dilanjutkan tanpa MUA.')

    biayaMUA = 0
    if booking is not None:
        biayaMUA = booking['harga']
    totalAwal = subtotal + biayaMUA
    minimalDP = hitungMinimalDP(totalAwal)

    cetakJudul('RINGKASAN AKHIR')
    print(f'Subtotal rental : {formatRupiah(subtotal)}')
    if booking is not None:
        print(f'Biaya MUA       : {formatRupiah(biayaMUA)} ({booking["kategori"]}, {booking["tanggal"]}, sesi {booking["sesi"]})')
    else:
        print(f'Biaya MUA       : {formatRupiah(0)}')
    print(f'Total awal      : {formatRupiah(totalAwal)}')
    print(f'Minimal DP 30%  : {formatRupiah(minimalDP)}')
    print('Batas bayar DP  : 24 jam sejak pesanan dibuat (lewat batas, pesanan batal otomatis)')

    if not inputYaTidak('\nSetuju membuat pesanan? (y/n): '):
        pesanInfo('Pesanan tidak dibuat.')
        return

    # simpan transaksi
    kodeRental = generateKode('RNT', bacaJSON(fileRental), 'kode')
    muaTersimpan = None
    if booking is not None:
        kodeMUA = tahanJadwalMUA(booking, kodeRental)
        if kodeMUA is None:
            pesanGagal('Sesi MUA baru saja terisi. Pesanan tidak dibuat, silakan ulangi.')
            return
        muaTersimpan = {'kodeMUA': kodeMUA, 'kodeLayanan': booking['kodeLayanan'],
                        'kategori': booking['kategori'], 'tanggal': booking['tanggal'],
                        'sesi': booking['sesi'], 'harga': booking['harga']}

    paketTersimpan = None
    if paket is not None:
        paketTersimpan = {'kode': paket['kode'], 'nama': paket['nama']}

    rental = {
        'kode': kodeRental,
        'idPelanggan': pelanggan['id'],
        'namaPelanggan': pelanggan['nama'],
        'dibuatPada': waktuSekarangTeks(),
        'batasBayar': batasBayarTeks(),
        'jenisPesanan': 'Paket' if paket is not None else 'Satuan',
        'paket': paketTersimpan,
        'items': items,
        'tanggalMulai': mulai,
        'tanggalAkhir': akhir,
        'durasi': durasi,
        'mua': muaTersimpan,
        'subtotalRental': subtotal,
        'biayaMUA': biayaMUA,
        'totalAwal': totalAwal,
        'minimalDP': minimalDP,
        'denda': 0,
        'totalAkhir': totalAwal,
        'totalDibayar': 0,
        'statusRental': 'ST-01',
        'statusBayar': 'PAY-01',
        'pengambilan': None,
        'pengembalian': None,
        'pengajuanBatal': False,
        'pembatalan': None
    }
    tambahData(fileRental, rental)

    pesanBerhasil('\nPesanan berhasil dibuat! Stok dan jadwal MUA ditahan sementara.')
    print(f'Kode rental     : {kodeRental}')
    if muaTersimpan is not None:
        print(f'Kode MUA        : {muaTersimpan["kodeMUA"]}')
    print(f'Total awal      : {formatRupiah(totalAwal)}')
    print(f'Minimal DP      : {formatRupiah(minimalDP)}')
    print(f'Batas bayar     : {rental["batasBayar"]}')

    if inputYaTidak('\nLanjut ke pembayaran sekarang? (y/n): '):
        process_payment(user, kodeRental)


# ---------- LIHAT TRANSAKSI (K) ----------

def daftarRentalUser(user):
    hasil = []
    for rental in bacaJSON(fileRental):
        if user['role'] == 'Pelanggan' and rental['idPelanggan'] != user['idPelanggan']:
            continue
        hasil.append(rental)
    return hasil


def show_transaction(user):
    cetakJudul('LIHAT TRANSAKSI')
    daftar = daftarRentalUser(user)
    if len(daftar) == 0:
        pesanInfo('Belum ada transaksi.')
        return
    tampilkanDaftarRental(daftar)
    while True:
        kode = input('\nKode rental (0 = kembali): ').strip().upper()
        if kode == '0':
            return
        rental = None
        for data in daftar:
            if data['kode'] == kode:
                rental = data
        if rental is None:
            pesanGagal('Kode rental tidak valid!')
            continue
        tampilkanDetailRental(rental)
        return


# ---------- KONFIRMASI PENGAMBILAN (O) ----------

def confirm_pickup(user):
    if not cekAkses(user, ('Admin', 'Petugas')):
        return
    cetakJudul('KONFIRMASI PENGAMBILAN')
    while True:
        kode = input('Kode rental (0 = kembali): ').strip().upper()
        if kode == '0':
            return
        rental = cariData(fileRental, 'kode', kode)
        if rental is None:
            pesanGagal('Kode rental tidak valid!')
        else:
            break

    tampilkanDetailRental(rental)
    if rental['statusRental'] != 'ST-02' or rental['totalDibayar'] < rental['minimalDP']:
        pesanGagal('Barang belum dapat diambil! Status harus ST-02 (DP minimal sudah dikonfirmasi).')
        return

    if not inputYaTidak('\nBarang sudah diperiksa dan diserahkan? (y/n): '):
        pesanInfo('Pengambilan belum dikonfirmasi.')
        return
    rental['statusRental'] = 'ST-03'
    rental['pengambilan'] = {'waktu': waktuSekarangTeks(), 'petugas': user['nama']}
    ubahData(fileRental, 'kode', kode, rental)
    pesanBerhasil('Pengambilan berhasil dikonfirmasi. Status menjadi ST-03 Sedang Disewa.')


# ---------- PEMBATALAN (Q) ----------

def batalkanRental(rental, jenis, oleh):
    rental['statusRental'] = 'ST-06'
    rental['pengajuanBatal'] = False
    rental['pembatalan'] = {'waktu': waktuSekarangTeks(), 'jenis': jenis,
                            'oleh': oleh, 'refund': 0}
    ubahData(fileRental, 'kode', rental['kode'], rental)
    lepasJadwalMUA(rental['kode'])


def ajukan_pembatalan(user):
    cetakJudul('AJUKAN PEMBATALAN')
    daftar = daftarRentalUser(user)
    tampilkanDaftarRental(daftar)
    kode = input('\nKode rental (0 = kembali): ').strip().upper()
    if kode == '0':
        return
    rental = None
    for data in daftar:
        if data['kode'] == kode:
            rental = data
    if rental is None:
        pesanGagal('Kode rental tidak valid!')
        return
    if rental['statusRental'] not in ('ST-01', 'ST-02'):
        pesanGagal('Pembatalan hanya dapat diajukan sebelum barang diambil (ST-01 atau ST-02).')
        return
    if rental['pengajuanBatal']:
        pesanInfo('Pengajuan pembatalan sudah tercatat dan menunggu konfirmasi.')
        return
    pesanInfo('Perhatian: pembatalan tidak mendapatkan pengembalian dana (no refund).')
    if not inputYaTidak('Ajukan pembatalan? (y/n): '):
        pesanInfo('Pengajuan dibatalkan.')
        return
    rental['pengajuanBatal'] = True
    ubahData(fileRental, 'kode', kode, rental)
    pesanBerhasil('Pengajuan pembatalan tercatat dan menunggu konfirmasi Petugas/Admin.')


def konfirmasi_pembatalan(user):
    cetakJudul('KONFIRMASI PEMBATALAN')
    pengajuan = []
    for rental in bacaJSON(fileRental):
        if rental['pengajuanBatal'] and rental['statusRental'] in ('ST-01', 'ST-02'):
            pengajuan.append(rental)
    if len(pengajuan) == 0:
        pesanInfo('Tidak ada pengajuan pembatalan.')
        return
    tampilkanDaftarRental(pengajuan)
    kode = input('\nKode rental (0 = kembali): ').strip().upper()
    if kode == '0':
        return
    rental = None
    for data in pengajuan:
        if data['kode'] == kode:
            rental = data
    if rental is None:
        pesanGagal('Kode rental tidak valid atau tidak ada pengajuan!')
        return
    pesanInfo('Pembatalan tidak mendapatkan refund. Stok dan jadwal MUA akan dilepas.')
    if not inputYaTidak('Setujui pembatalan? (y/n): '):
        pesanInfo('Konfirmasi pembatalan dibatalkan.')
        return
    batalkanRental(rental, 'Manual', user['nama'])
    pesanBerhasil(f'Transaksi {kode} dibatalkan (ST-06). Reservasi stok dan jadwal MUA dilepas.')


def cancel_rental(user):
    if user['role'] == 'Pelanggan':
        ajukan_pembatalan(user)
    else:
        konfirmasi_pembatalan(user)


def check_auto_cancellation():
    # pesanan ST-01 yang melewati batas 24 jam tanpa DP terkonfirmasi dibatalkan otomatis
    dataRental = bacaJSON(fileRental)
    sekarang = datetime.now()
    jumlah = 0
    for rental in dataRental:
        if rental['statusRental'] != 'ST-01':
            continue
        batas = ubahWaktu(rental['batasBayar'])
        if batas is not None and sekarang > batas and rental['totalDibayar'] < rental['minimalDP']:
            batalkanRental(rental, 'Otomatis', 'Sistem')
            jumlah += 1
    if jumlah > 0:
        pesanInfo(f'{jumlah} pesanan dibatalkan otomatis karena DP belum dibayar dalam 24 jam.')
    return jumlah
