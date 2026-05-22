# Cookie Consent

This project ships with a LGPD/GDPR-compliant cookie consent flow that gates non-essential cookies (such as Google Analytics) behind explicit user consent.

## Configuration

Two settings control the feature in `pyaa/settings/dev.py`:

1. `GOOGLE_ANALYTICS_ID`: the Google Analytics 4 Measurement ID (prefix: `G-xxxxxxxxxx`). When empty, the GA loader partial is not rendered.
2. `COOKIE_CONSENT_VERSION`: a string that identifies the current version of the cookie policy.

Both can be defined directly in `dev.py` or provided as environment variables (`APP_GOOGLE_ANALYTICS_ID`).

## Versioning Consent Decisions

`COOKIE_CONSENT_VERSION` is exposed to the frontend through `window.PYAA_COOKIE_CONSENT_VERSION` and stored alongside each consent decision in `localStorage`.

Whenever the cookie policy changes (new categories, new vendors, updated wording in the privacy policy), bump this value. The frontend will detect the mismatch on the next page load, discard the previous decision, and show the banner again so the user can re-consent.

Example:

```python
# pyaa/settings/dev.py
COOKIE_CONSENT_VERSION = "2"
```

## Categories

| Category   | Always on | Description                                                              |
|------------|-----------|--------------------------------------------------------------------------|
| Essential  | Yes       | Authentication, security and base site functionality.                    |
| Analytics  | No        | Google Analytics. Loaded only after the user grants explicit consent.    |

To add a new optional category:

1. Append the key to `OPTIONAL_CATEGORIES` in `apps/web/static/js/cookie-consent.js`.
2. Add a toggle row in `templates/partials/cookie_consent.html` using `data-category="<key>"`.
3. Listen for the `cookie-consent:updated` event in the partial that loads the related vendor script.

## Google Analytics Loader

The script in `templates/partials/google_analytics.html` follows Google Consent Mode v2:

- Sets `ga-disable-<ID>` to `true` and consent defaults to `denied` on every page load.
- Listens for the `cookie-consent:updated` window event.
- When `analytics` is granted, lazily injects `gtag/js` and calls `gtag('consent', 'update', { analytics_storage: 'granted' })`.
- When consent is revoked, sets the disable flag back to `true` and updates consent to `denied`.

## Changing Preferences

Users can change their decision at any time through the **Cookie Settings** link in the footer, which opens the same preferences modal used during the initial decision.
