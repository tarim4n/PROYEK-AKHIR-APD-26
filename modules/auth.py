import pwinput
from utils.database import bacaJSON, tambahData, cariData, ubahData, fileUser
from utils.helpers import generateKode
from utils.display import (cetakJudul, cetakMenu, pesanBerhasil, pesanGagal,
                           pesanInfo, tampilkanTabel, tungguEnter)
from utils.validation import (inputTeks, inputHP, inputPilihanMenu, cekAkses)
from modules.customers import (buatPelanggan, inputPassword, inputUsernameBaru)


def register():
    cetakJudul('REGISTER PELANGGAN')
    username = inputUsernameBaru()
    if username == '0':
        pesanInfo('Registrasi dibatalkan.')
        return
    password = inputPassword('Password (min 6 karakter): ')
    nama = inputTeks('Nama lengkap: ')
    hp = inputHP('Nomor HP: ')

    pelanggan = buatPelanggan(username, password, nama, hp)
    pesanBerhasil('Registrasi berhasil!')
    print(f'ID pelanggan Anda: {pelanggan["id"]}')


def login():
    percobaan = 0
    batasPercobaan = 3

    while percobaan < batasPercobaan:
        cetakJudul('LOGIN')
        username = inputTeks('Username: ').lower()
        user = cariData(fileUser, 'username', username)

        if user is None:
            percobaan += 1
            pesanGagal(f'Username tidak ditemukan! Percobaan {percobaan}/{batasPercobaan}')
            continue

        password = pwinput.pwinput('Password: ', mask='*')
        if password != user['password']:
            percobaan += 1
            pesanGagal(f'Password salah! Percobaan {percobaan}/{batasPercobaan}')
            continue

        if not user['aktif']:
            percobaan += 1
            pesanGagal(f'Akun nonaktif tidak dapat login! Percobaan {percobaan}/{batasPercobaan}')
            continue

        pesanBerhasil(f'Login berhasil. Selamat datang, {user["nama"]}!')
        return user

    pesanGagal('Kesempatan login habis. Silakan registrasi akun terlebih dahulu.')
    register()
    return None


def add_account():
    cetakJudul('TAMBAH AKUN')
    username = inputUsernameBaru()
    if username == '0':
        pesanInfo('Penambahan akun dibatalkan')
        return
    password = inputPassword('Password (min 6 karakter): ')
    nama = inputTeks('Nama lengkap: ')
    print('Role: 1. Admin  2. Petugas')
    pilihan = inputPilihanMenu('Pilih role: ', ('1', '2'))
    if pilihan == '1':
        role = 'Admin'
    else:
        role = 'Petugas'

    akun = {
        'id': generateKode('USR', bacaJSON(fileUser), 'id'),
        'username': username,
        'password': password,
        'nama': nama,
        'role': role,
        'aktif': True
    }
    tambahData(fileUser, akun)
    pesanBerhasil(f'Akun {role} berhasil dibuat dengan ID {akun["id"]}.')


def show_accounts():
    baris = []
    for akun in bacaJSON(fileUser):
        if akun['aktif']:
            status = 'Aktif'
        else:
            status = 'Nonaktif'
        baris.append([akun['id'], akun['username'], akun['nama'], akun['role'], status])
    tampilkanTabel(['ID', 'Username', 'Nama', 'Role', 'Status'], baris)


def update_role(userLogin):
    cetakJudul('UBAH ROLE AKUN')
    show_accounts()
    username = inputTeks('Username akun (0 = batal): ').lower()
    if username == '0':
        return
    akun = cariData(fileUser, 'username', username)
    if akun is None:
        pesanGagal('Akun tidak ditemukan!')
        return
    if akun['username'] == userLogin['username']:
        pesanGagal('Anda tidak dapat mengubah role akun Anda sendiri!')
        return
    if akun['role'] == 'Pelanggan':
        pesanGagal('Role akun Pelanggan tidak dapat diubah.')
        return

    print(f'Role saat ini: {akun["role"]}')
    print('Role baru: 1. Admin  2. Petugas')
    pilihan = inputPilihanMenu('Pilih role baru: ', ('1', '2'))
    if pilihan == '1':
        akun['role'] = 'Admin'
    else:
        akun['role'] = 'Petugas'
    ubahData(fileUser, 'username', username, akun)
    pesanBerhasil(f'Role akun {username} diubah menjadi {akun["role"]}.')


def toggle_account(userLogin):
    cetakJudul('AKTIFKAN/NONAKTIFKAN AKUN')
    show_accounts()
    username = inputTeks('Username akun (0 = batal): ').lower()
    if username == '0':
        return
    akun = cariData(fileUser, 'username', username)
    if akun is None:
        pesanGagal('Akun tidak ditemukan!')
        return
    if akun['username'] == userLogin['username']:
        pesanGagal('Anda tidak dapat menonaktifkan akun Anda sendiri!')
        return

    akun['aktif'] = not akun['aktif']
    ubahData(fileUser, 'username', username, akun)
    if akun['aktif']:
        pesanBerhasil(f'Akun {username} diaktifkan.')
    else:
        pesanBerhasil(f'Akun {username} dinonaktifkan.')


def manage_accounts(user):
    if not cekAkses(user, ('Admin',)):
        return
    while True:
        cetakJudul('KELOLA AKUN')
        cetakMenu(['1. Tambah Akun', '2. Ubah Role Akun',
                   '3. Aktifkan/Nonaktifkan Akun', '4. Lihat Daftar Akun', '0. Kembali'])
        pilihan = inputPilihanMenu('Pilih menu: ', ('1', '2', '3', '4', '0'))
        if pilihan == '0':
            return
        elif pilihan == '1':
            add_account()
        elif pilihan == '2':
            update_role(user)
        elif pilihan == '3':
            toggle_account(user)
        else:
            cetakJudul('DAFTAR AKUN')
            show_accounts()
        tungguEnter()
