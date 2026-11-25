from utils.database import bacaJSON, fileUser
from utils.helpers import ubahTanggal, tanggalKeTeks
from utils.display import pesanGagal


def inputTeks(pesan):
    while True:
        teks = input(pesan).strip()
        if teks == '':
            pesanGagal('Input tidak boleh kosong!')
        else:
            return teks


def inputAngka(pesan, minimal=0):
    while True:
        try:
            angka = int(input(pesan).strip())
            if angka < minimal:
                pesanGagal(f'Angka minimal {minimal}!')
            else:
                return angka
        except ValueError:
            pesanGagal('Input harus berupa angka bulat!')


def inputYaTidak(pesan):
    while True:
        jawaban = input(pesan).strip().lower()
        if jawaban in ('y', 'ya'):
            return True
        elif jawaban in ('n', 'tidak', 't'):
            return False
        pesanGagal('Jawab dengan y atau n!')


def inputPilihanMenu(pesan, daftarPilihan):
    while True:
        pilihan = input(pesan).strip()
        if pilihan in daftarPilihan:
            return pilihan
        pesanGagal('Pilihan tidak valid! Silakan coba lagi.')


def inputTanggal(pesan, boleh0=False):
    while True:
        teks = input(pesan).strip()
        if boleh0 and teks == '0':
            return '0'
        tanggal = ubahTanggal(teks)
        if tanggal is None:
            pesanGagal('Format tanggal salah! Gunakan DD-MM-YYYY, contoh 25-12-2026.')
        else:
            return tanggalKeTeks(tanggal)


def validasiHP(hp):
    if not hp.isdigit():
        return False, 'Nomor HP hanya boleh berisi angka!'
    if not hp.startswith('08'):
        return False, 'Nomor HP harus diawali 08!'
    if len(hp) < 12:
        return False, 'Nomor HP minimal 12 digit!'
    if len(hp) > 15:
        return False, 'Nomor HP maksimal 15 digit!'
    return True, ''


def inputHP(pesan):
    while True:
        hp = input(pesan).strip()
        valid, alasan = validasiHP(hp)
        if valid:
            return hp
        pesanGagal(alasan)


def usernameSudahAda(username):
    dataUser = bacaJSON(fileUser)
    for user in dataUser:
        if user['username'] == username:
            return True
    return False


def cekAkses(user, daftarRole):
    if user['role'] in daftarRole:
        return True
    pesanGagal('Akses ditolak! Anda tidak memiliki hak akses ke menu ini.')
    return False