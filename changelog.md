# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0-Beta] - 2026-02-07 - BREAKING ARCHITECTURE RELEASE

#### > ⚠️ Major redesign of core architecture, path system, plugin system, and infrastructure boundaries.

### 💥 Breaking Changes

- Root system diubah dari relative/path-based menjadi pyproject.toml–based auto discovery

- ROOT tidak lagi static manual path → diganti dynamic resolver berbasis pyproject.toml

- Struktur data/ dipindahkan ke Bowlplate-scoped root (BOWLPLATE_ROOT)

- Plugin loader rewritten (directory traversal logic dirombak total)

- SQLite initialization fixed: db path vs folder confusion resolved

---

### 🧩 Core System Overhaul

Introduced:

ROOT (project root resolver)

SRC_ROOT

BOWLPLATE_ROOT

Path handling fully migrated toward pathlib.Path

Legacy os.path.join usage significantly reduced

---

### 🔌 Plugin System v2

Plugin loader redesigned:

recursive scanning fixed

manifest detection stabilized (manifest.json)

plugin module isolation improved

Plugin structure standardized:

plugins/<module>/<plugin>/manifest.json

---

### 🗄 Database Layer Fixes

Fixed SQLite fatal bug:

os.makedirs() mistakenly targeting file path instead of directory

Database initialization now correctly ensures:

parent directory exists

DB file is not treated as folder

---

### 🧪 Testing Infrastructure

Pytest integration stabilized

Test discovery now functional

Fixed “no tests ran” misinterpretation phase

---

### 🧱 Infrastructure Improvements

Added safer filesystem resolution strategy

Improved compatibility between Windows/Linux path handling

Reduced dependency on runtime CWD (current working directory)

---

### 🐞 Bug Fixes (Major)

Fixed sqlite3.OperationalError: unable to open database file

Fixed plugin path overwriting bug in recursive traversal

Fixed ROOT misalignment causing wrong data directory resolution

Fixed missing manifest detection due to path mutation

---

### ⚠️ Known Beta Notes

Plugin API is still unstable (subject to change in 2.x beta series)

Internal modules are not fully frozen (no ABI guarantee yet)

Some legacy path assumptions may still exist in test modules

---

## [1.6.0] - 2026-22-06

### Added

- Universal Configuration (Sqlite3 integration & JSON data).

### Update

- `Bootstrap.py` moved to `/bootstrap/` at root workspace.

## [1.1.1] - 2026-26-05

### Added

- Database Integration (SQLAlchemy) (In Development) (unreleased and unbeta, is really on development :v)
- Update readme.md
- Make requirements.txt compatibilities for `pip` PM
- update structure repo with place all of ecosystem application to `src`

## [1.0.0] - 2026-03-05

### Added

- Core WebServer & Controller
- Web interface with clean structure
- Database integration (JsonDB)
- Environment configuration support (.env)
- Professional logger system
- Comprehensive project documentation

### Infrastructure

- Clean architecture pattern (domain/infrastructure/application layers)
- Modular code structure for scalability
- Organized folder layout (assets, tests, configurations)
- Changelog tracking (this file)

### Documentation

- Code comments and docstrings
- .env.example for configuration reference

### Known Issues

- (Any limitations? List them)
- currently not scalable
- low level protection
- rate limit bypass
- form not secured
- web login not secured
