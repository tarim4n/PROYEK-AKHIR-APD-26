try:
    import prettytable
    import colorama
    import pwinput
except ImportError:
    print('Library belum terpasang. Jalankan perintah berikut:')
    print('python3 -m pip install prettytable colorama pwinput matplotlib')
    raise SystemExit

from utils.database import cekFileJSON
from utils.display import (cetakJudul, cetakMenu, tampilkanWelcome, pesanInfo,
                           pesanGagal, tungguEnter)
from utils.validation import inputPilihanMenu
from modules.auth import login, register, manage_accounts
from modules.catalog import show_catalog, manage_categories, manage_products
from modules.customers import manage_customers
from modules.mua import manage_mua
from modules.packages import manage_packages
from modules.rental import (create_rental, show_transaction, confirm_pickup,
                            cancel_rental, check_auto_cancellation)
from modules.payment import process_payment
from modules.return_item import process_return, check_late_status
from modules.reports import menu_reports


def menu_data_master(user):
    # Flowchart halaman 8 (H)
    while True:
        cetakJudul('KELOLA DATA MASTER')
        cetakMenu(['1. Kategori', '2. Katalog', '3. Layanan MUA', '4. Paket Acara', '0. Kembali'])
        pilihan = inputPilihanMenu('Pilih menu: ', ('1', '2', '3', '4', '0'))
        if pilihan == '0':
            return
        elif pilihan == '1':
            manage_categories(user)
        elif pilihan == '2':
            manage_products(user)
        elif pilihan == '3':
            manage_mua(user)
        else:
            manage_packages(user)


def menu_admin(user):
    # Flowchart halaman 5 (E)
    while True:
        cetakJudul(f'MENU ADMIN - {user["nama"]}')
        cetakMenu(['1. Kelola Data Master', '2. Kelola Akun',
                   '3. Buat Rental/Paket Acara + MUA', '4. Lihat Seluruh Transaksi',
                   '5. Konfirmasi Pembayaran', '6. Konfirmasi Pengambilan',
                   '7. Kelola Pengembalian dan Denda', '8. Kelola Pembatalan Transaksi',
                   '9. Laporan dan Statistik', '10. Logout'])
        pilihan = inputPilihanMenu('Pilih menu: ', ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10'))
        if pilihan == '1':
            menu_data_master(user)
        elif pilihan == '2':
            manage_accounts(user)
        elif pilihan == '3':
            create_rental(user)
            tungguEnter()
        elif pilihan == '4':
            show_transaction(user)
            tungguEnter()
        elif pilihan == '5':
            process_payment(user)
            tungguEnter()
        elif pilihan == '6':
            confirm_pickup(user)
            tungguEnter()
        elif pilihan == '7':
            process_return(user)
            tungguEnter()
        elif pilihan == '8':
            cancel_rental(user)
            tungguEnter()
        elif pilihan == '9':
            menu_reports(user)
        else:
            pesanInfo('Logout berhasil.')
            return


def menu_petugas(user):
    # Flowchart halaman 6 (F)
    while True:
        cetakJudul(f'MENU PETUGAS - {user["nama"]}')
        cetakMenu(['1. Lihat Katalog', '2. Kelola/Cari Pelanggan',
                   '3. Buat Rental/Paket Acara + MUA', '4. Lihat Transaksi',
                   '5. Konfirmasi Pembayaran', '6. Konfirmasi Pengambilan',
                   '7. Pengembalian dan Denda', '8. Konfirmasi Pembatalan',
                   '9. Laporan (Akses Terbatas)', '10. Logout'])
        pilihan = inputPilihanMenu('Pilih menu: ', ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10'))
        if pilihan == '1':
            show_catalog()
            tungguEnter()
        elif pilihan == '2':
            manage_customers(user)
        elif pilihan == '3':
            create_rental(user)
            tungguEnter()
        elif pilihan == '4':
            show_transaction(user)
            tungguEnter()
        elif pilihan == '5':
            process_payment(user)
            tungguEnter()
        elif pilihan == '6':
            confirm_pickup(user)
            tungguEnter()
        elif pilihan == '7':
            process_return(user)
            tungguEnter()
        elif pilihan == '8':
            cancel_rental(user)
            tungguEnter()
        elif pilihan == '9':
            menu_reports(user)
        else:
            pesanInfo('Logout berhasil.')
            return


def menu_pelanggan(user):
    # Flowchart halaman 7 (G)
    while True:
        cetakJudul(f'MENU PENGGUNA - {user["nama"]}')
        cetakMenu(['1. Lihat Katalog/Cari Kategori', '2. Buat Rental/Paket Acara + MUA',
                   '3. Lihat Transaksi Saya', '4. Ajukan Pembatalan', '5. Logout'])
        pilihan = inputPilihanMenu('Pilih menu: ', ('1', '2', '3', '4', '5'))
        if pilihan == '1':
            show_catalog()
            tungguEnter()
        elif pilihan == '2':
            create_rental(user)
            tungguEnter()
        elif pilihan == '3':
            show_transaction(user)
            tungguEnter()
        elif pilihan == '4':
            cancel_rental(user)
            tungguEnter()
        else:
            pesanInfo('Logout berhasil.')
            return


def main():
    # Flowchart halaman 1 (A)
    cekFileJSON()
    while True:
        # pemeriksaan otomatis: pembatalan 24 jam dan keterlambatan
        check_auto_cancellation()
        check_late_status()

        tampilkanWelcome()
        cetakJudul('MAIN MENU')
        cetakMenu(['1. Login', '2. Register', '3. Katalog', '4. Keluar'])
        pilihan = inputPilihanMenu('Pilih menu: ', ('1', '2', '3', '4'))

        if pilihan == '1':
            user = login()
            if user is not None:
                if user['role'] == 'Admin':
                    menu_admin(user)
                elif user['role'] == 'Petugas':
                    menu_petugas(user)
                else:
                    menu_pelanggan(user)
                continue
        elif pilihan == '2':
            register()
        elif pilihan == '3':
            show_catalog()
        else:
            print('Terima kasih telah menggunakan RUPAÉ. Sampai jumpa!')
            break
        tungguEnter()


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print('\nProgram dihentikan.')
