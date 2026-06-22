# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.6.0] - 2026-22-96 
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
