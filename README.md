# CustomBase-Flask 🚀

A flexible and customizable Flask-based boilerplate for building modern web applications — with clean architecture, environment config support, database integration, and a professional logger system built in.
##### [ NOT RECOMMENDED USING FOR PROD OR OTHERS PROJECT ]
##### [ THIS IS FOR LEARNING ]
---

## 📦 Tech Stack

| Package         | Purpose                         |
| --------------- | ------------------------------- |
| `Flask`         | Core web framework              |
| `SQLAlchemy`    | Database ORM                    |
| `python-dotenv` | Environment variable management |
| `Werkzeug`      | Utilities & security helpers    |
| `pydantic`      | Data validation                 |
| `aiohttp`       | Async HTTP client               |
| `bleach`        | Input sanitization              |
| `psutil`        | System monitoring               |
| `Requests`      | HTTP requests                   |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- `pip` or `conda`

### Installation

1. Clone the repository:

```bash
git clone https://github.com/LetnanGM/CustomBase-Flask.git
cd CustomBase-Flask
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

if you use conda:

```bash
# pip
pip install -r requirements.txt

# conda
conda install --yes --file requirements.yaml
```

## Project Structure

wait update on structure, we will make it scalable and no errors about import ;D

the structure project created on [structure](./STRUCTURE.md)

## Configuration

Copy `.env.example` to `.env` and update with your settings:

4. Copy the environment config:

```bash
cp .env.example .env
```

Edit `.env` sesuai konfigurasi kamu.

---

## ▶️ Running the Application

Semua ekosistem aplikasi ada di folder `src/`. Masuk dulu ke sana:

```bash
cd src/
python -m bowlplate.main
```

Aplikasi akan berjalan di `http://localhost:5000`.

> Untuk mengubah host atau port, edit file `src/bowlplate/data/config/server/server.json`.

---

## 🗂️ Project Structure

structure project terdapat pada [structure.md](./STRUCTURE.md)

> ⚠️ Struktur ini masih dalam pengembangan dan akan diperbarui agar lebih scalable.

---

## ⚙️ Configuration

Salin file `.env.example` ke `.env` dan isi sesuai kebutuhan:

```bash
cp ./src/bowlplate/.env.example ./src/bowlplate/.env
```

---

## 📋 Changelog

Lihat [changelog.md](./changelog.md) untuk riwayat perubahan lengkap.

Versi terbaru: **v1.6.0** — Universal Configuration (SQLite3 & JSON data integration).

---

## ⚠️ Known Issues (v2.0.0)

- Belum fully scalable
- Proteksi masih level rendah
- Rate limit bisa di-bypass
- Form belum aman
- Web login belum aman

- run harus di folder /src/

Issues di atas sedang dalam roadmap pengembangan.

---

## 🗺️ Roadmap

- [x] Core WebServer & Controller
- [x] Database integration (JsonDB)
- [x] Environment configuration support (.env)
- [x] Professional logger system
- [x] SQLAlchemy integration (In Development)
- [x] Universal Configuration (SQLite3 + JSON)
- [ ] Rate limiting & form security
- [ ] Authentication module
- [ ] API documentation (Swagger)
- [ ] Docker support

---

## 🤝 Contributing

Kontribusi sangat diterima! Silakan buka issue atau pull request.

---

## 📄 License

Proyek ini open source di bawah lisensi **MIT**.
