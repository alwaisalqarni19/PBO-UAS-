# 🌲 Forest of Fate

> Game RPG 2D berbasis tile menggunakan **Python + Pygame** Ujian Akhir Semester Pemrograman Berorientasi Objek

---

## 👥 Anggota Kelompok

| No | Nama | NIM |
|----|------|-----|
| 1  | *(Salsabila Putri Ariska)* | *(25051204252)* |
| 2  | *(Al-Wais Alqarn)*         | *(25051204013)* |
| 3  | *(Aliya Zalva Rosida)*     | *(25051204017)* |
| 3  | *(Fikri Khair Rahmansyah)* | *(25051204212)* |



---

## 📖 Deskripsi Project

**Forest of Fate** adalah game RPG aksi 2D top-down yang dibangun menggunakan Python dan library Pygame. Pemain berperan sebagai seorang pahlawan yang bertugas membersihkan Hutan Fate dari ancaman monster. Game ini menerapkan sistem dua fase pertempuran: mengalahkan gerombolan musuh biasa (kroco) terlebih dahulu, lalu menghadapi boss besar yang bersembunyi di kedalaman hutan.

Game menampilkan sistem combat lengkap dengan berbagai senjata dan sihir, sistem upgrade karakter, efek partikel, antarmuka pengguna (HUD), serta layar menu yang interaktif dengan efek transisi pixel.

---

## ✨ Fitur Utama

- **Sistem Combat** — Serang musuh dengan 5 jenis senjata (Sword, Lance, Axe, Rapier, Sai) dan 2 jenis sihir (Flame, Heal)
- **Sistem Dua Fase** — Fase 1 melawan musuh biasa (Bamboo, Spirit, Squid), Fase 2 menghadapi Boss (Raccoon)
- **Upgrade Karakter** — Tingkatkan 5 atribut: Health, Energy, Attack, Magic, dan Speed menggunakan EXP
- **HUD Lengkap** — Tampilan health bar, energy bar, exp counter, slot senjata & sihir aktif, serta counter musuh tersisa
- **Kamera Y-Sort** — Kamera mengikuti pemain dengan pengurutan sprite berdasarkan posisi Y untuk kedalaman visual
- **Efek Partikel** — Animasi partikel untuk serangan, sihir, kematian musuh, dan interaksi rumput
- **Invincibility Frame** — Pemain dan musuh mendapat jeda kebal setelah terkena serangan
- **Dukungan Gamepad** — Kontrol joystick/controller selain keyboard
- **Layar Menu Interaktif** — Start screen, How to Play, Story, Phase Intro dengan navigasi tombol BACK/NEXT dan efek transisi pixel
- **Musik & Efek Suara** — BGM, suara serangan, kematian, heal, dan efek sound untuk setiap aksi

---

## 🎮 Kontrol

| Aksi | Keyboard | Gamepad |
|------|----------|---------|
| Gerak | `W A S D` / Arrow Keys | Left Stick / D-Pad |
| Serang | `SPACE` | Button A (0) |
| Sihir | `CTRL Kiri` | Button B (1) |
| Ganti Senjata | `Q` | LB (4) |
| Ganti Sihir | `E` | RB (5) |
| Menu Upgrade | `M` | — |
| Navigasi Menu | `SPACE` / `BACKSPACE` | Button A / B |

---

## 🚀 Cara Menjalankan Project

### Prasyarat

- Python **3.10+**
- Library `pygame` terinstall

### Instalasi

```bash
# 1. Clone atau ekstrak repository
git clone <url-repository>
cd PBO-UAS--main

# 2. Install dependensi
pip install pygame

# 3. Jalankan game dari folder code/
cd code
python main.py
```

> **Penting:** Game **harus dijalankan dari dalam folder `code/`** agar path ke aset (grafis, audio, map) dapat ditemukan dengan benar.

---

## 🏗️ Struktur Project

```
PBO-UAS--main/
├── code/
│   ├── main.py        # Entry point & game loop utama
│   ├── level.py       # Manajemen level, map, fase, & logika game
│   ├── player.py      # Kelas Player
│   ├── enemy.py       # Kelas Enemy
│   ├── entity.py      # Kelas dasar Entity (parent Player & Enemy)
│   ├── weapon.py      # Kelas Weapon
│   ├── magic.py       # Kelas MagicPlayer
│   ├── ui.py          # Kelas UI (HUD)
│   ├── upgrade.py     # Kelas Upgrade & Item
│   ├── particles.py   # Kelas AnimationPlayer & ParticleEffect
│   ├── tile.py        # Kelas Tile
│   ├── support.py     # Fungsi utilitas (import CSV, folder)
│   ├── settings.py    # Konstanta & data game (senjata, musuh, magic)
│   └── debug.py       # Fungsi debug overlay
├── graphics/          # Aset gambar (sprite, UI, tilemap, efek)
├── audio/             # Aset suara (BGM, SFX)
└── map/               # File CSV peta game
```

---

## 🧩 Penjelasan Implementasi OOP

Project ini menerapkan konsep-konsep utama Pemrograman Berorientasi Objek secara menyeluruh:

### 1. Inheritance (Pewarisan)

Hierarki kelas dibangun dengan `Entity` sebagai kelas induk bagi entitas yang dapat bergerak di dunia game.

```
pygame.sprite.Sprite
        │
      Entity          ← base class: gerakan, collision, animasi frame
      /    \
  Player   Enemy      ← mewarisi movement & collision dari Entity
```

- **`Entity`** (`entity.py`) mewarisi `pygame.sprite.Sprite` dan mendefinisikan logika umum: pergerakan (`move`), deteksi tabrakan (`collision`), dan efek berkedip saat terkena serangan (`wave_value`).
- **`Player`** (`player.py`) mewarisi `Entity` dan menambahkan: input keyboard/gamepad, sistem senjata & sihir, manajemen stamina, dan animasi 12 arah.
- **`Enemy`** (`enemy.py`) mewarisi `Entity` dan menambahkan: AI state machine (idle → move → attack), statistik dari data monster, dan suara spesifik per monster.

### 2. Encapsulation (Enkapsulasi)

Setiap kelas membungkus data dan perilakunya sendiri:

- **`Player`** menyimpan `stats`, `health`, `energy`, `exp`, dan `weapon_index` secara internal. Akses dari luar melalui method seperti `get_full_weapon_damage()` dan `get_full_magic_damage()`.
- **`Enemy`** mengelola `health`, `vulnerable`, `attack_cooldown`, dan `invincibility_duration` secara mandiri dalam method `cooldowns()` dan `check_death()`.
- **`UI`** (`ui.py`) mengenkapsulasi semua logika rendering HUD (health bar, energy bar, exp, slot item) tanpa mengekspos detail implementasinya ke luar.
- **`Upgrade`** (`upgrade.py`) membungkus logika menu upgrade termasuk navigasi dan perhitungan biaya upgrade.

### 3. Polymorphism (Polimorfisme)

- Method `update()` diimplementasikan berbeda di setiap kelas sprite. Pygame memanggil `update()` secara seragam lewat `sprite.Group.update()`, namun hasilnya berbeda: `Player.update()` memproses input dan cooldown, `Enemy.update()` menjalankan AI dan check kematian, `ParticleEffect.update()` menganimasikan dan menghapus dirinya sendiri.
- Method `enemy_update(player)` hanya dimiliki oleh `Enemy`, dipanggil secara selektif oleh `YSortCameraGroup.enemy_update()` menggunakan `hasattr` untuk memastikan hanya enemy yang mendapat update AI.

### 4. Abstraksi

- **`Entity`** mengabstraksikan mekanik fisika dasar (gerak & collision) sehingga `Player` dan `Enemy` tidak perlu mengulang kode yang sama.
- **`AnimationPlayer`** (`particles.py`) mengabstraksikan pembuatan efek partikel. Kelas lain cukup memanggil `create_particles(type, pos, groups)` tanpa perlu tahu detail frame animasi.
- **`MagicPlayer`** (`magic.py`) mengabstraksikan logika sihir. `Level` cukup memanggil `magic_player.heal()` atau `magic_player.flame()`.
- **`YSortCameraGroup`** (`level.py`) mengabstraksikan sistem kamera dan rendering dengan Y-sorting, diwarisi dari `pygame.sprite.Group`.

### 5. Composition (Komposisi)

Kelas-kelas kompleks dibangun dari objek-objek yang lebih kecil:

- **`Level`** memiliki (`has-a`): `Player`, banyak `Enemy`, banyak `Tile`, `UI`, `Upgrade`, `AnimationPlayer`, `MagicPlayer`, dan `YSortCameraGroup`.
- **`Game`** (`main.py`) memiliki: `Level` dan semua state machine menu.
- **`Player`** memiliki referensi ke fungsi callback (`create_attack`, `destroy_attack`, `create_magic`) yang disediakan oleh `Level`, memisahkan tanggung jawab antar kelas.

---

## 📸 Screenshot Tampilan Program


### 🏠 Start Screen
<img width="1599" height="895" alt="image" src="https://github.com/user-attachments/assets/a3815bbd-29cf-4ca9-9050-24e8205b41ce" />


### 📜 Story & How to Play
<img width="1600" height="898" alt="image" src="https://github.com/user-attachments/assets/27b1ccb9-4cbd-4a3e-bbb6-5b78cf1aba0c" />
<img width="1536" height="1024" alt="image" src="https://github.com/user-attachments/assets/ed8d874c-ac71-4b9f-a805-4ff458254173" />


### ⚔️ Gameplay Fase 1 (Melawan Kroco)
<img width="1598" height="896" alt="image" src="https://github.com/user-attachments/assets/eb54cb92-7d03-4bd0-a723-afaa4046ad82" />


### 👹 Gameplay Fase 2 (Boss Fight)
<img width="1597" height="885" alt="image" src="https://github.com/user-attachments/assets/64480d9c-760d-4b92-ac0e-a76112104a08" />

 
### 📊 Menu Upgrade
<img width="1592" height="894" alt="image" src="https://github.com/user-attachments/assets/cbf4d818-5c5a-42d5-afc3-0e3d5600fd21" />


### 🏆 Victory / Game Over Screen
<img width="1594" height="896" alt="Screenshot 2026-06-01 205930" src="https://github.com/user-attachments/assets/230219eb-bd47-4a36-b80a-5f9675046878" /><img width="1595" height="892" alt="image" src="https://github.com/user-attachments/assets/299b6cf1-37cd-4da9-b69b-be922dc5c37a" />


---

## 🛠️ Teknologi yang Digunakan

- **Python 3.10+**
- **Pygame** — rendering, input, audio, sprite management
- **CSV** — format data peta tile

---

## 📝 Catatan Pengembangan

- Resolusi layar: `1280 × 720` px, target `60 FPS`
- Ukuran tile: `64 × 64` px
- Peta dibuat dengan Tiled Map Editor dan diekspor ke format CSV
- Sistem phase menggunakan flag `_phase2_triggered` untuk memastikan boss hanya di-spawn sekali saat semua musuh fase 1 habis
