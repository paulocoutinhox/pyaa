<p align="center">
    <a href="https://github.com/paulocoutinhox/pyaa" target="_blank" rel="noopener noreferrer">
        <img width="250" src="extras/images/logo.png" alt="PyAA Logo">
    </a>
    <br>
    PyAA - Python Advanced Application
    <br>
</p>

PyAA is a powerful, open-source Python + Django template application designed to build robust web applications with all the essential features pre-built. Whether you need a site, an e-commerce platform, or a SaaS application, PyAA has you covered – for free!

[![Build](https://github.com/paulocoutinhox/pyaa/actions/workflows/build.yml/badge.svg)](https://github.com/paulocoutinhox/pyaa/actions/workflows/build.yml)

[![codecov](https://codecov.io/gh/paulocoutinhox/pyaa/graph/badge.svg?token=KQ1H9SVD4Y)](https://codecov.io/gh/paulocoutinhox/pyaa)

## 🚀 Features

- **User Management** – Handle user registration, login, profile management, account recovery, configurable account activation, and more.
- **Subscription Management** – Manage user subscriptions by credits or expiration date.
- **Credit System** – Support for selling and managing user credits.
- **Checkout System** – Complete payment flow for products and services.
- **Digital Products** – Sell digital products with secure download links after purchase.
- **Banner System** – Manage banners with view and click tracking, plus detailed reporting in the admin panel.
- **Admin Panel** – A fully functional admin dashboard for managing the application.
- **Theme Selector** – Support for light, dark, and auto theme modes.
- **Email Integration** – Send transactional emails with ease.
- **Recaptcha Support** – Enhance security with Recaptcha integration.
- **Image Gallery** – Manage a gallery of images efficiently.
- **Static Content Management** – Organize and manage static content across your site.
- **System Logs** – Comprehensive logging system with multiple levels (debug, info, success, warning, error) and categorization.
- **Multi-language Support** – Easily handle multiple languages.
- **Multiple Currency Support** – Process payments in different currencies.
- **Stripe Integration** – Seamlessly manage subscription payments and one-time purchases through Stripe.
- **Subscription Plans** – Control and configure different subscription tiers.
- **Background Queue** – Powered by DjangoQ with worker support for handling asynchronous tasks.
- **Status Color System** – Visual indicators for various statuses throughout the application.
- **Cached Paginator** – Optimized pagination for better performance.
- **Docker Support** – Docker configurations for web application and cron jobs.
- **Test Coverage** – Over 50% test coverage, ensuring reliability and robustness.
- **Versatile Use** – Perfect for building websites, e-commerce platforms, or SaaS products.

## 💻 How To Use

Execute the following commands:

```
make deps
make setup
make migrate
make create-su
make fixtures
make run
```

## 📚 Documentation

- [API](docs/api.md)
- [Database](docs/database.md)
- [Docker](docs/docker.md)
- [Ngrok](docs/ngrok.md)
- [Production](docs/production.md)
- [Security](docs/security.md)
- [Stripe](docs/stripe.md)
- [Troubleshooting](docs/troubleshooting.md)
- [WebApp](docs/webapp.md)
- [Cron](docs/cron.md)
- [Queue](docs/queue.md)

## 🛡️ License

[MIT](http://opensource.org/licenses/MIT)

Copyright (c) 2024-2025, Paulo Coutinho
