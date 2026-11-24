import json
import os
import sys

baseDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dataDIR = os.path.join(baseDIR, 'data')

fileKategori = os.path.join(dataDIR, 'categories.json')
fileProduk = os.path.join(dataDIR, 'products.json')
fileMUA = os.path.join(dataDIR, 'mua_services.json')
filePaket = os.path.join(dataDIR, 'packages.json')
fileUser = os.path.join(dataDIR, 'users.json')
filePelanggan = os.path.join(dataDIR, 'customers.json')
fileRental = os.path.join(dataDIR, 'rentals.json')
filePembayaran = os.path.join(dataDIR, 'payments.json')

semuaFile = (fileKategori, fileProduk, fileMUA, filePaket,
             fileUser, filePelanggan, fileRental, filePembayaran)


def bacaJSON(namaFile):
    try:
        with open(namaFile, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f'File {namaFile} tidak ditemukan. File kosong dibuat.')
        simpanJSON(namaFile, [])
        return []
    except json.JSONDecodeError:
        print(f'File JSON rusak: {namaFile}')
        print('Perbaiki isi file tersebut, lalu jalankan program lagi.')
        sys.exit()


def simpanJSON(namaFile, data):
    try:
        with open(namaFile, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        return True
    except OSError:
        print('Data gagal disimpan ke file JSON!')
        return False


def cekFileJSON():
    if not os.path.exists(dataDIR):
        os.makedirs(dataDIR)
    for namaFile in semuaFile:
        if not os.path.exists(namaFile):
            print(f'Peringatan: {namaFile} tidak ada. File kosong dibuat.')
            simpanJSON(namaFile, [])


def tambahData(namaFile, dataBaru):
    data = bacaJSON(namaFile)
    data.append(dataBaru)
    return simpanJSON(namaFile, data)


def cariData(namaFile, kunci, nilai):
    data = bacaJSON(namaFile)
    for item in data:
        if item[kunci] == nilai:
            return item
    return None


def ubahData(namaFile, kunci, nilai, dataBaru):
    data = bacaJSON(namaFile)
    for index in range(len(data)):
        if data[index][kunci] == nilai:
            data[index] = dataBaru
            return simpanJSON(namaFile, data)
    return False


def hapusData(namaFile, kunci, nilai):
    data = bacaJSON(namaFile)
    dataBaru = []
    for item in data:
        if item[kunci] != nilai:
            dataBaru.append(item)
    if len(dataBaru) == len(data):
        return False
    return simpanJSON(namaFile, dataBaru)
