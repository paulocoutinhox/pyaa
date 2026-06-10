# Passing Data from Django to JavaScript

## The problem

Django runs on the **server** (Python). Your JavaScript runs in the **browser**. They are two separate worlds and do not share variables. So when a value exists in Django — the current language, a configuration flag, some text — and your JavaScript needs it, you have to **hand it over through the HTML page** that Django sends to the browser.

The old way was to drop a `<script>` in the template like `window.PYAA_LANGUAGE = '{{ LANGUAGE_CODE }}'`. We do **not** do that anymore, because it mixes logic into templates and creates global variables that can clash. Instead, Django writes the data into the HTML as plain data, and the JavaScript reads it.

There are four ways to do this. They go from "one small value" to "a whole translation system". Pick by **how much** data you have:

```
One or two simple values (a word, number, true/false)?
   → it belongs to the whole app      → Pattern 1
   → it belongs to one element        → Pattern 2

A whole object, a list, or several text strings?
   → Pattern 3 (json_script)

The JavaScript itself needs to translate lots of text (with plurals)?
   → Pattern 4 (JavaScript catalog)
```

---

## Pattern 1 — One app-wide value (`data-*` on `<html>`)

**Use it when:** you have a simple value (a single word, number, or true/false) that the whole app might need — like the language, a version, an analytics id, or a feature flag.

**How it works:** an HTML element can carry custom data in a `data-*` attribute. We put these on the `<html>` tag (the top of the page, available everywhere). The browser exposes every `data-*` through `element.dataset`. We read them once in `config.js` and any module can import them.

**1. Put the value on `<html>`** (`templates/layouts/base.html`):

```django
<html lang="{{ LANGUAGE_CODE }}"
    data-cookie-consent-version="{{ cookie_consent_version }}"
    data-analytics-id="{{ analytics_id }}"
    class="h-full">
```

**2. Read it once** in `apps/web/static/vendor/frontend/js/config.js`:

```js
// document.documentElement is the <html> element
export const language = document.documentElement.lang || "";
export const analyticsId =
    document.documentElement.dataset.analyticsId || "";
```

**3. Use it anywhere** by importing:

```js
import { analyticsId } from "./config.js";
```

> **Watch the name:** in HTML it is kebab-case, in JavaScript it becomes camelCase.
> `data-analytics-id` → `dataset.analyticsId`.

---

## Pattern 2 — A value that belongs to one element

**Use it when:** the data is not global — it belongs to a specific thing on the page. Think of a list of banners where **each** banner has its own token and link. Putting that on `<html>` makes no sense — it belongs on each banner element.

**How it works:** same `data-*` idea, but you put the attribute on the element itself, and the module that handles that feature reads it from the element it is working with.

**Template** (`templates/partials/banners.html`) — each banner carries its own data:

```django
<a href="javascript:void(0);" data-banner-click
    data-banner-token="{{ banner.token }}"
    data-banner-link="{{ banner.link|default:'' }}"
    data-banner-target-blank="{{ banner.target_blank|lower }}"></a>
```

**Module** (`apps/web/static/vendor/frontend/js/banners.js`) — reads from the clicked element:

```js
element.addEventListener("click", (event) => {
    event.preventDefault();

    const token = element.dataset.bannerToken;
    const link = element.dataset.bannerLink || "";
    const external = element.dataset.bannerTargetBlank === "true";
    // ... use token / link / external
});
```

> Rule of thumb: **app-wide → Pattern 1**, **per-element → Pattern 2**.

---

## Pattern 3 — An object, a list, or many strings (`json_script`)

**Use it when:** you have more than one or two values — a configuration object, a list, or a set of text strings (for example, messages you want translated). You cannot comfortably cram an object into a single attribute, so you ship it as JSON.

**How it works:** Django has a filter called **`json_script`**. It takes a Python value (a dict, list, etc.), turns it into JSON, and writes it inside a special tag:

```html
<script id="js-messages" type="application/json">{"saved": "Saved successfully"}</script>
```

Two important things:
- `type="application/json"` means the browser treats it as **plain text data, not code** — it never runs it.
- Django **escapes** dangerous characters, so even a malicious value cannot inject a script. It is safe by design.

Your JavaScript grabs that text and turns it back into a real object with `JSON.parse`.

This is perfect for **translated strings**: you translate them in Python (where `gettext` already knows the user's language) and send the finished text to JS.

**1. Build the value on the server** (a view or a context processor):

```python
from django.utils.translation import gettext_lazy as _

js_messages = {
    "confirm_delete": _("Are you sure?"),
    "saved": _("Saved successfully"),
}
```

**2. Render it** in a template (a partial included once, e.g. in `base.html`):

```django
{{ js_messages|json_script:"js-messages" }}
```

**3. Read it** in a small module, e.g. `apps/web/static/vendor/frontend/js/messages.js`:

```js
const element = document.getElementById("js-messages");

// .textContent is the JSON text; JSON.parse turns it into a JS object
export const messages = element ? JSON.parse(element.textContent) : {};
```

**4. Use it:**

```js
import { messages } from "./messages.js";

alert(messages.confirm_delete);
```

> The translation stays in your normal `.po`/`gettext` workflow. JavaScript only reads the result — it never translates anything itself.

---

## Pattern 4 — Full translation system in JavaScript (`JavaScriptCatalog`)

**Use it when:** the JavaScript itself has to translate a **lot** of text on its own, including plurals (`"1 item"` vs `"5 items"`) and inserting values into sentences. Listing every string by hand (Pattern 3) would be too much.

**How it works:** Django can automatically build a translation "dictionary" for the browser from your `.po` files and give your JavaScript the familiar `gettext()` function.

**1. Add a URL** (`pyaa/urls.py`):

```python
from django.views.i18n import JavaScriptCatalog

path(
    "jsi18n/",
    JavaScriptCatalog.as_view(packages=["apps.web"]),
    name="javascript-catalog",
),
```

**2. Load it** before your bundle (in `head.html`):

```django
<script src="{% url 'javascript-catalog' %}"></script>
```

**3. Translate in JavaScript:**

```js
gettext("Hello");
ngettext("1 item", "%s items", count);   // handles plurals
interpolate(gettext("Hello %s"), [name]); // inserts values
```

> **Trade-off:** this adds `gettext`/`ngettext` as global functions (a script provided by Django). It is the standard Django approach, but less "clean" than the patterns above. Prefer Pattern 3 unless the JavaScript-side translations really grow.

---

## Quick summary

| What you have | Use | Why |
|---|---|---|
| One value for the whole app | `data-*` on `<html>` + `config.js` | simplest, read once, import anywhere |
| One value tied to an element | `data-*` on the element | the data belongs to that element |
| An object / list / a few strings | `json_script` | ships JSON safely, translated on the server |
| Lots of translations in JS | `JavaScriptCatalog` | full `gettext` in the browser |

**The two rules of the project:**
- Never assign to `window.*`.
- Never put behavior in templates (no `onclick`, no inline `<script>` with logic). A data-only `<script type="application/json">` block is fine, because it is data, not behavior.
