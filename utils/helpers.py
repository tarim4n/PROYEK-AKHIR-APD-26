from datetime import datetime, timedelta

formatTanggal = '%d-%m-%Y'
formatWaktu = '%d-%m-%Y %H:%M'

namaStatusRental = {
    'ST-01': 'Menunggu Pembayaran',
    'ST-02': 'Menunggu Pengambilan',
    'ST-03': 'Sedang Disewa',
    'ST-04': 'Terlambat',
    'ST-05': 'Selesai',
    'ST-06': 'Dibatalkan'
}

namaStatusBayar = {
    'PAY-01': 'Belum Bayar',
    'PAY-02': 'DP',
    'PAY-03': 'Lunas'
}

# status transaksi yang masih menahan stok
statusAktif = ('ST-01', 'ST-02', 'ST-03', 'ST-04')


def generateKode(awalan, daftarData, kunci='kode'):
    angkaTerbesar = 0
    for data in daftarData:
        bagian = data[kunci].split('-')
        if data[kunci].startswith(awalan + '-') and bagian[-1].isdigit():
            if int(bagian[-1]) > angkaTerbesar:
                angkaTerbesar = int(bagian[-1])
    return f'{awalan}-{angkaTerbesar + 1:03d}'


def formatRupiah(angka):
    if angka is None:
        return 'Belum diatur'
    return 'Rp' + f'{angka:,}'.replace(',', '.')


def ubahTanggal(teks):
    try:
        return datetime.strptime(teks, formatTanggal)
    except ValueError:
        return None


def ubahWaktu(teks):
    try:
        return datetime.strptime(teks, formatWaktu)
    except ValueError:
        return None


def tanggalKeTeks(tanggal):
    return tanggal.strftime(formatTanggal)


def hariIni():
    sekarang = datetime.now()
    return sekarang.replace(hour=0, minute=0, second=0, microsecond=0)


def waktuSekarangTeks():
    return datetime.now().strftime(formatWaktu)


def batasBayarTeks():
    batas = datetime.now() + timedelta(hours=24)
    return batas.strftime(formatWaktu)


def hitungDurasi(tanggalMulai, tanggalAkhir):
    mulai = ubahTanggal(tanggalMulai)
    akhir = ubahTanggal(tanggalAkhir)
    return (akhir - mulai).days + 1


def periodeBertabrakan(mulai1, akhir1, mulai2, akhir2):
    return mulai1 <= akhir2 and mulai2 <= akhir1


def hitungMinimalDP(totalAwal):
    # 30% dari total awal, dibulatkan ke atas
    return -(-totalAwal * 30 // 100)


def hitungStatusBayar(totalDibayar, totalAkhir):
    if totalDibayar <= 0:
        return 'PAY-01'
    elif totalDibayar < totalAkhir:
        return 'PAY-02'
    return 'PAY-03'
