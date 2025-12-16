# VT Automation Scanner

Dokumen ini menjelaskan penggunaan dan desain teknis **VT Automation Scanner**, sebuah alat otomasi untuk melakukan enrichment domain menggunakan **VirusTotal API** dengan pendekatan terkontrol terhadap quota, rate limit, dan risiko pemblokiran API key.

---

## Tujuan

VT Automation Scanner dirancang untuk:

* Melakukan pemindaian **domain, URL, atau domain dari email** menggunakan VirusTotal
* Mengambil ringkasan hasil analisis berupa rasio `malicious/total engine`
* Mengelola **multi API key** secara otomatis (round-robin)
* Mengurangi konsumsi quota melalui **mekanisme cache lokal**
* Menghasilkan output yang siap digunakan pada **Excel maupun laporan analisis**

---

## Fitur Utama

* Dukungan multi API key
* Perhitungan delay otomatis untuk menghindari rate limit
* Mekanisme retry dengan exponential backoff
* Cache lokal berbasis JSON untuk mencegah pemindaian ulang
* Input fleksibel (paste manual atau file Excel)
* Output file Excel dan clipboard

---

## Dependensi

Pastikan seluruh dependensi berikut telah terpasang:

```bash
pip install vt-py pandas openpyxl python-dotenv tqdm pyperclip
```

Catatan:

* Modul `pyperclip` diperlukan untuk fitur penyalinan hasil ke clipboard.

---

## Konfigurasi API Key

Buat file `.env` pada direktori yang sama dengan script:

```env
VT_APIKEY1=API_KEY_ANDA
VT_APIKEY2=API_KEY_CADANGAN
```

Rekomendasi:

* Gunakan lebih dari satu API key untuk dataset berukuran besar
* Hindari penggunaan API key pribadi untuk kebutuhan tim
* Jangan membagikan file `.env`

---

## Format Input

### Opsi 1 – Input Manual

Pengguna dapat langsung menempelkan (paste) domain, URL, atau email setelah menjalankan script. Tekan **Enter dua kali** untuk memulai proses pemindaian.

Contoh input:

```
example.com
https://suspicious-site.net/login
admin@domain-test.org
```

### Opsi 2 – File Excel

Gunakan file `input.xlsx` dengan kolom wajib berikut:

| Domain      |
| ----------- |
| example.com |

---

## Alur Kerja Sistem

1. Membersihkan input dan mengekstrak domain
2. Memeriksa keberadaan domain pada cache lokal
3. Melakukan request ke VirusTotal jika domain belum pernah dipindai
4. Mengambil data `last_analysis_stats`
5. Menyimpan hasil ke cache dan file output

---

## Output

### File Excel

Hasil pemindaian disimpan dalam file:

```
output_vt_scan.xlsx
```

Kolom tambahan yang dihasilkan:

| VT_Score |
| -------- |
| =2/94    |

Format menggunakan tanda `=` bertujuan untuk menjaga konsistensi saat diproses di Microsoft Excel.

### Clipboard

Setelah proses selesai, pengguna dapat memilih:

1. Menyalin Domain dan VT_Score
2. Menyalin VT_Score saja
3. Keluar dari program

---

## Rate Limit dan Keamanan

Delay antar request dihitung secara otomatis berdasarkan jumlah API key:

```
(60 / (4 × jumlah_api_key)) + buffer
```

Pendekatan ini bertujuan untuk meminimalkan risiko:

* Rate limit
* Quota habis
* Pemblokiran API key

---

## Kesalahan Umum yang Perlu Dihindari

* Melakukan pemindaian skala besar dengan satu API key
* Menghapus cache lalu memindai ulang dataset yang sama
* Menghilangkan delay antar request

Praktik tersebut dapat menyebabkan API key dibatasi atau dinonaktifkan.

---

## Struktur File

| File                | Deskripsi                      |
| ------------------- | ------------------------------ |
| input.xlsx          | Data domain yang akan dipindai |
| output_vt_scan.xlsx | Hasil pemindaian VirusTotal    |
| vt_cache.json       | Cache lokal hasil pemindaian   |
| .env                | Penyimpanan API key            |

---

## Troubleshooting

**Clipboard tidak berfungsi**

```bash
pip install pyperclip
```

**Quota API habis**

* Tunggu hingga quota tersedia kembali
* Tambahkan API key tambahan

**Error Banned**

* API key telah diblokir
* Ganti dengan API key baru

---

## Catatan Akhir

VT Automation Scanner ditujukan untuk kebutuhan:

* Cyber Threat Intelligence (CTI)
* Analisis keamanan
* Incident response
* Penyusunan laporan teknis

Hasil pemindaian VirusTotal bersifat **indikatif** dan harus dianalisis lebih lanjut sebelum dijadikan dasar pengambilan keputusan keamanan.
