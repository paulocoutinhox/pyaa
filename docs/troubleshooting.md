# Troubleshooting

Some problems that you can find and their solutions.

## Production Setup With Docker

When you setup this app in production with docker, you need configure somethings to make it work:

```bash
mkdir -p logs && chmod -R 777 logs
mkdir -p cache && chmod -R 777 cache
mkdir -p static && chmod -R 777 static
mkdir -p media && chmod -R 777 media
```

If you use SQLite:

```bash
mkdir -p db && chmod -R 777 db
```

## MySQL Client On Apple System

Install MySQL Client on macOS with the commands:

```bash
brew install mysql-client pkg-config
export PKG_CONFIG_PATH="/opt/homebrew/opt/mysql-client/lib/pkgconfig"
python3 -m pip install mysqlclient
```

## WeasyPrint

Install the WeasyPrint libraries to generate reports.

Official website: https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation

**macOS:**

```bash
brew install weasyprint
```

**Ubuntu Linux:**

```bash
apt install weasyprint
```

**Windows:**

Download latest release here: https://github.com/Kozea/WeasyPrint/releases
