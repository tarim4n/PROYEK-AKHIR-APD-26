import pwinput
from utils.database import (bacaJSON, tambahData, cariData, ubahData,
                            filePelanggan, fileUser)
from utils.helpers import generateKode
from utils.display import (cetakJudul, cetakMenu, pesanBerhasil, pesanGagal,
                           pesanInfo, tampilkanTabel, tungguEnter)
from utils.validation import (inputTeks, inputHP, inputPilihanMenu,
                              usernameSudahAda, validasiHP, cekAkses)


def inputPassword(pesan):
    while True:
        password = pwinput.pwinput(pesan, mask='*')
        if len(password) < 6:
            pesanGagal('Password minimal 6 karakter!')
        else:
            return password


def inputUsernameBaru():
    # mengembalikan username unik, atau '0' jika dibatalkan
    while True:
        username = inputTeks('Username (0 = batal): ').lower()
        if username == '0':
            return '0'
        if ' ' in username:
            pesanGagal('Username tidak boleh mengandung spasi!')
        elif usernameSudahAda(username):
            pesanGagal('Username sudah digunakan! Pilih username lain.')
        else:
            return username


def buatPelanggan(username, password, nama, hp):
    dataPelanggan = bacaJSON(filePelanggan)
    dataUser = bacaJSON(fileUser)
    idPelanggan = generateKode('CUS', dataPelanggan, 'id')
    idUser = generateKode('USR', dataUser, 'id')

    akun = {
        'id': idUser,
        'username': username,
        'password': password,
        'nama': nama,
        'role': 'Pelanggan',
        'aktif': True,
        'idPelanggan': idPelanggan
    }
    pelanggan = {
        'id': idPelanggan,
        'username': username,
        'nama': nama,
        'hp': hp
    }
    tambahData(fileUser, akun)
    tambahData(filePelanggan, pelanggan)
    return pelanggan


def tampilkanPelanggan(daftar):
    baris = []
    for pelanggan in daftar:
        baris.append([pelanggan['id'], pelanggan['nama'], pelanggan['hp'], pelanggan['username']])
    tampilkanTabel(['ID', 'Nama', 'No. HP', 'Username'], baris)


def find_customer():
    cetakJudul('CARI PELANGGAN')
    kataKunci = inputTeks('Masukkan nama atau ID CUS: ').lower()
    hasil = []
    for pelanggan in bacaJSON(filePelanggan):
        if kataKunci in pelanggan['nama'].lower() or kataKunci == pelanggan['id'].lower():
            hasil.append(pelanggan)
    if len(hasil) == 0:
        pesanGagal('Pelanggan tidak ditemukan!')
    else:
        tampilkanPelanggan(hasil)


def register_customer():
    cetakJudul('DAFTARKAN PELANGGAN')
    username = inputUsernameBaru()
    if username == '0':
        pesanInfo('Pendaftaran dibatalkan.')
        return
    password = inputPassword('Password (min 6 karakter): ')
    nama = inputTeks('Nama lengkap: ')
    hp = inputHP('Nomor HP: ')
    pelanggan = buatPelanggan(username, password, nama, hp)
    pesanBerhasil(f'Pelanggan berhasil didaftarkan dengan ID {pelanggan["id"]}.')


def update_customer():
    cetakJudul('UBAH DATA PELANGGAN')
    tampilkanPelanggan(bacaJSON(filePelanggan))
    idPelanggan = inputTeks('Masukkan ID CUS (0 = batal): ').upper()
    if idPelanggan == '0':
        return
    pelanggan = cariData(filePelanggan, 'id', idPelanggan)
    if pelanggan is None:
        pesanGagal('ID pelanggan tidak ditemukan!')
        return

    print(f'Nama saat ini : {pelanggan["nama"]}')
    print(f'No. HP        : {pelanggan["hp"]}')
    print('Kosongkan input jika tidak ingin mengubah.')
    namaBaru = input('Nama baru: ').strip()
    hpBaru = input('No. HP baru: ').strip()

    if hpBaru != '':
        valid, alasan = validasiHP(hpBaru)
        if not valid:
            pesanGagal(alasan)
            return
        pelanggan['hp'] = hpBaru
    if namaBaru != '':
        pelanggan['nama'] = namaBaru

    ubahData(filePelanggan, 'id', idPelanggan, pelanggan)
    # nama di akun login ikut diperbarui
    akun = cariData(fileUser, 'username', pelanggan['username'])
    if akun is not None:
        akun['nama'] = pelanggan['nama']
        ubahData(fileUser, 'username', akun['username'], akun)
    pesanBerhasil('Data pelanggan berhasil diubah.')


def manage_customers(user):
    if not cekAkses(user, ('Admin', 'Petugas')):
        return
    while True:
        cetakJudul('KELOLA PELANGGAN')
        cetakMenu(['1. Cari Pelanggan', '2. Daftarkan Pelanggan',
                   '3. Ubah Data Pelanggan', '0. Kembali'])
        pilihan = inputPilihanMenu('Pilih menu: ', ('1', '2', '3', '0'))
        if pilihan == '0':
            return
        elif pilihan == '1':
            find_customer()
        elif pilihan == '2':
            register_customer()
        else:
            update_customer()
        tungguEnter()
