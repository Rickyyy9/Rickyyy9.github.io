# Portofolio — Rickyyy9

Website portofolio statis (HTML + CSS + JS vanilla) yang otomatis menampilkan
**semua repository GitHub** pemilik akun, dan di-hosting gratis di GitHub Pages.

Live: https://rickyyy9.github.io

---

## Struktur

```
portofolio/
├── index.html              # halaman utama (ada marker PROJECTS:START/END)
├── style.css               # semua styling, responsive
├── generate_projects.py    # ambil repo dari GitHub API -> render kartu proyek
├── assets/                 # foto profil & gambar proyek
│   └── foto-profil.jpg     # (taruh fotomu di sini)
├── .nojekyll               # biar GitHub Pages tidak memproses lewat Jekyll
└── README.md
```

## Update daftar proyek

Setiap kali ada repo baru / deskripsi berubah:

```bash
cd ~/portofolio
python3 generate_projects.py          # semua repo (public + private)
python3 generate_projects.py --public-only   # hanya yang public
git add -A && git commit -m "update proyek" && git push
```

Script ini butuh token: otomatis diambil dari `gh auth token`.
Tanpa token tetap jalan, tapi cuma repo **public** (rate limit 60/jam).

**Catatan privasi:** dengan mode default, repo *private* ikut tampil sebagai
kartu berlabel `PRIVATE` tanpa link (nama repo terlihat publik, isi tidak).
Kalau tidak mau nama repo privat terekspos, jalankan `--public-only`.

## Kustomisasi cepat

| Yang mau diubah | Di mana |
|---|---|
| Nama & tagline hero | `index.html` bagian `<section class="hero">` |
| Foto profil | ganti `assets/foto-profil.jpg` |
| Teks "Tentang Saya" | `<section id="tentang">` |
| Email / LinkedIn | `<section id="kontak">` |
| Warna utama | `style.css` → cari `#3498db` (biru) & `#e74c3c` (merah tombol) |

## Deploy manual (kalau tidak pakai git push)

1. Buat repo baru bernama `Rickyyy9.github.io` (harus public).
2. Upload `index.html`, `style.css`, folder `assets/`, dan `.nojekyll`.
3. Settings → Pages → Source: branch `main`, folder `/ (root)` → Save.
4. Tunggu ~1 menit, buka https://rickyyy9.github.io

## Form kontak

Form di bagian kontak masih statis (belum kirim email). Untuk aktif:
daftar gratis di [formspree.io](https://formspree.io), lalu ganti tag form jadi:

```html
<form class="contact-form" action="https://formspree.io/f/XXXXXXX" method="POST">
```
