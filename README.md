# CustomBase-Flask 🚀

A flexible and customizable Flask-based foundation for building modern web applications.

## Overview

CustomBase-Flask is a starter template that provides a solid foundation for Flask projects with best practices, common utilities, and a clean project structure. It's designed to help you get up and running quickly while maintaining code quality and scalability.

## Features

- 🎯 **Clean Project Structure** - Well-organized folder layout
- 🔧 **Configuration Management** - Environment-based configurations
- 🛡️ **Security Best Practices** - Built-in security features
- 📝 **Logging System** - Comprehensive logging setup
- 🧪 **Testing Ready** - Pre-configured for unit testing
- 🎨 **Customizable** - Easy to adapt to your needs

## Getting Started

### Prerequisites

- Python 3.8+
- pip or conda

### Installation

1. Clone the repository:

```bash
git clone https://github.com/LetnanGM/CustomBase-Flask.git
cd CustomBase-Flask
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

if you use conda:

```bash
conda install --yes --file requirements.yaml
```

### Running the Application

`src` folder is all of ecosystem application, change the directory after install dependencies.

```bash
cd src/
```

then run this

```bash
python main.py
```

The application will start at `http://localhost:5000`
you can change the host and port on `data/configuration/internal/server/webapp.py'

## Project Structure

wait update on structure, we will make it scalable and no errors about import ;D
maybe, the structure project we will created on [structure](./STRUCTURE.md)

```
CustomBase-Flask/
├── app.py              # Main application entry point
├── requirements.txt    # Project dependencies
├── .env.example        # Environment variables template
├── README.md          # This file
├── CONTRIBUTOR.md     # Contribution guidelines
└── src/
    ├── __init__.py
    ├── config.py      # Configuration management
    ├── routes/        # Route definitions
    ├── models/        # Database models
    └── utils/         # Utility functions
```

## Configuration

Copy `.env.example` to `.env` and update with your settings:

```bash
cp .env.example .env
```

## Running Tests

```bash
pytest
```

## Contributing

We welcome contributions from the community! Please see [CONTRIBUTOR.md](CONTRIBUTOR.md) for detailed guidelines on how to contribute.

## License

This project is open source and available under the MIT License.

## Support

For questions, issues, or suggestions, please [open an issue](https://github.com/LetnanGM/CustomBase-Flask/issues) on GitHub.

## Roadmap

- [ ] API documentation with Swagger
- [ ] Database ORM integration
- [ ] Authentication module
- [ ] Frontend template integration
- [ ] Docker support

---

**Happy coding!** 💻
