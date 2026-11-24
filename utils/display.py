import os
from colorama import Fore, init
from prettytable import PrettyTable

init(autoreset=True)


def clearTerminal():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


def tungguEnter():
    input('\nTekan Enter untuk melanjutkan...')
    clearTerminal()


def cetakJudul(teks):
    garis = '=' * 60
    print(Fore.CYAN + '\n' + garis)
    print(Fore.CYAN + teks.center(60))
    print(Fore.CYAN + garis)


def cetakMenu(daftarMenu):
    for menu in daftarMenu:
        print(Fore.YELLOW + menu)


def pesanBerhasil(pesan):
    print(Fore.GREEN + pesan)


def pesanGagal(pesan):
    print(Fore.RED + pesan)


def pesanInfo(pesan):
    print(Fore.YELLOW + pesan)


def tampilkanTabel(kolom, baris, kolomKanan=()):
    if len(baris) == 0:
        pesanInfo('Data belum tersedia.')
        return
    tabel = PrettyTable()
    tabel.field_names = kolom
    tabel.align = 'l'
    for namaKolom in kolomKanan:
        tabel.align[namaKolom] = 'r'
    for barisData in baris:
        tabel.add_row(barisData)
    print(tabel)


def tampilkanWelcome():
    cetakJudul('WELCOME TO RUPAÉ')
    print(Fore.CYAN + 'Every Look Has Its Own Story\n')
    print('Temukan penampilan terbaikmu bersama RUPAÉ.')
    print('Kami hadir untuk menemani setiap momen spesial melalui berbagai pilihan')
    print('busana, aksesori, dan layanan tata rias yang sesuai dengan ceritamu.\n')
    print(Fore.CYAN + 'Your style, Your Story, Your Moment.')
