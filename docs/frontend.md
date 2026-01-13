# Frontend

This project uses **Tailwind CSS v4** for styling and **esbuild** for JavaScript bundling. The build pipeline is managed by npm.

## Architecture

The frontend architecture follows this structure:

```
apps/web/static/vendor/frontend/
├── css/
│   └── frontend.css     # Tailwind import and custom CSS (input file)
├── js/
│   └── frontend.js      # JavaScript entry point (input file)
└── output/
    ├── bundle.css       # Final compiled CSS (output file, DO NOT edit manually)
    └── bundle.js        # Final bundled JavaScript (output file, DO NOT edit manually)

apps/web/static/css/
├── main.scss            # SCSS entry point for non-Tailwind custom overrides
└── custom.scss          # Project-specific custom styles (non-Tailwind)
```

## Configuration Files

### tailwind.config.js

Tailwind scans all HTML templates and JavaScript files:

```javascript
export default {
  darkMode: 'class',
  content: [
    './templates/**/*.html',
    './apps/web/static/vendor/frontend/js/**/*.js'
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

### package.json

Two main build modes with parallel CSS and JS building:

```json
{
  "scripts": {
    "frontend:dev": "npm-run-all --parallel css:dev js:dev",
    "frontend:prod": "npm run css:prod && npm run js:prod",
    "css:dev": "npx @tailwindcss/cli -i ./apps/web/static/vendor/frontend/css/frontend.css -o ./apps/web/static/vendor/frontend/output/bundle.css --watch",
    "css:prod": "npx @tailwindcss/cli -i ./apps/web/static/vendor/frontend/css/frontend.css -o ./apps/web/static/vendor/frontend/output/bundle.css --minify",
    "js:dev": "esbuild ./apps/web/static/vendor/frontend/js/frontend.js --bundle --outfile=./apps/web/static/vendor/frontend/output/bundle.js --sourcemap --watch",
    "js:prod": "esbuild ./apps/web/static/vendor/frontend/js/frontend.js --bundle --outfile=./apps/web/static/vendor/frontend/output/bundle.js --minify"
  }
}
```

## Build Commands

The project provides two build modes:

### Development with Watch Mode

For active development with automatic rebuilding:

```bash
make frontend-dev
```

or:

```bash
npm run frontend:dev
```

Watches for changes in HTML templates, JavaScript files, and the Tailwind input file. Runs CSS and JS builds in parallel.

### Production Build (Minified)

For production deployment with minified CSS and JS:

```bash
make frontend-prod
```

or:

```bash
npm run frontend:prod
```

**Important**: Always use `make frontend-prod` before committing frontend changes. The minified bundles should be committed to avoid rebuilding in Docker.

## Workflow

### Development Workflow

1. Start the frontend watchers:
   ```bash
   make frontend-dev
   ```

2. Start the Django server:
   ```bash
   make run
   ```

3. Edit HTML templates, CSS files, or JavaScript files
4. Changes automatically compile to bundle files

### Before Committing

Always generate the production version:

```bash
make frontend-prod
git add apps/web/static/vendor/frontend/output/bundle.css
git add apps/web/static/vendor/frontend/output/bundle.js
git commit -m "update frontend"
```

This ensures optimized CSS and JS are available in production without requiring a build step in Docker.

## Using Tailwind CSS

### Basic Usage

Use Tailwind utility classes directly in templates:

```html
<div class="flex items-center justify-between p-4 rounded-lg shadow-md">
    <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
        Hello World
    </h1>
    <button class="px-4 py-2 text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors">
        Click me
    </button>
</div>
```

### Layout

```html
<div class="container mx-auto px-4">
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div class="p-6 bg-white rounded-lg shadow">Card 1</div>
        <div class="p-6 bg-white rounded-lg shadow">Card 2</div>
        <div class="p-6 bg-white rounded-lg shadow">Card 3</div>
    </div>
</div>
```

### Responsive Design

```html
<div class="text-sm md:text-base lg:text-lg">
    Responsive text
</div>

<div class="hidden md:block">
    Visible on medium screens and up
</div>
```

## Dark Mode

### Configuration

Dark mode is configured in `tailwind.config.js`:

```javascript
export default {
  darkMode: 'class',
  // ...
}
```

### Usage

Add the `dark` class to the `<html>` element:

```html
<html class="dark">
```

Use Tailwind's `dark:` variant:

```html
<div class="bg-white dark:bg-gray-900">
  <h1 class="text-gray-900 dark:text-white">Title</h1>
  <p class="text-gray-700 dark:text-gray-300">Content</p>
  <button class="bg-blue-600 dark:bg-blue-500">Button</button>
</div>
```

### Color Palette

Tailwind provides comprehensive color palettes:

```html
<!-- Grays -->
<div class="bg-gray-50">Lightest</div>
<div class="bg-gray-100">...</div>
<div class="bg-gray-900">Darkest</div>

<!-- Colors -->
<div class="bg-blue-500">Blue</div>
<div class="bg-green-500">Green</div>
<div class="bg-red-500">Red</div>
<div class="bg-yellow-500">Yellow</div>
```

## Customizing Tailwind

### In frontend.css

Add Tailwind customizations in `vendor/frontend/css/frontend.css`:

```css
@import "tailwindcss";

/* custom CSS classes */
.btn-primary {
  padding: 0.5rem 1rem;
  background-color: #2563eb;
  color: white;
  border-radius: 0.5rem;

  &:hover {
    background-color: #1d4ed8;
  }
}

.text-shadow {
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
}
```

**Note**: Tailwind CSS v4 uses `@import "tailwindcss"` instead of the old `@tailwind` directives. Custom classes should be written as regular CSS, not using `@apply` or `@layer`.

## Non-Tailwind Styles (custom.scss)

The `custom.scss` file is for styles **completely outside of Tailwind**. This file should NOT use `@apply` or any Tailwind features.

### When to Use custom.scss

- Styles that cannot be converted to Tailwind
- Third-party library overrides
- Complex SCSS features (mixins, functions, variables)
- Styles that need to exist independently of Tailwind

### Example

```scss
// custom.scss - NO Tailwind here!
.component {
  padding: 16px;
  background-color: #ffffff;
  border-left: 4px solid #3b82f6;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15);
  }
}
```

## JavaScript Bundling

### frontend.js Structure

The `vendor/frontend/js/frontend.js` file is the entry point for all JavaScript:

```javascript
// vendor imports (optional), example:
// import 'preline';
// import 'jquery';

// app code
document.addEventListener('DOMContentLoaded', () => {
  console.log('frontend loaded');
});
```

### Adding JavaScript Libraries

Install via npm and import in `frontend.js`:

```bash
npm install library-name
```

```javascript
// in frontend.js
import 'library-name';
// or
import { specificFunction } from 'library-name';
```

esbuild will automatically bundle all imports into `bundle.js`.

### Using in Templates

The bundles are already included in the base template:

```html
<link rel="stylesheet" href="{% static 'vendor/frontend/output/bundle.css' %}">
<script src="{% static 'vendor/frontend/output/bundle.js' %}" defer></script>
```

## Extending Tailwind

### Custom Colors

Add custom colors in `tailwind.config.js`:

```javascript
export default {
  theme: {
    extend: {
      colors: {
        primary: '#1a1a1a',
        secondary: '#e0e1e2',
      },
    },
  },
}
```

Use them:

```html
<div class="bg-primary text-white">Custom color</div>
```

### Custom Spacing

```javascript
export default {
  theme: {
    extend: {
      spacing: {
        '72': '18rem',
        '84': '21rem',
        '96': '24rem',
      },
    },
  },
}
```

### Custom Fonts

```javascript
export default {
  theme: {
    extend: {
      fontFamily: {
        sans: ['Nunito Sans', 'sans-serif'],
      },
    },
  },
}
```

## Dependencies

Required npm packages:

```json
{
  "devDependencies": {
    "@tailwindcss/cli": "latest",
    "esbuild": "latest",
    "npm-run-all": "latest"
  }
}
```

Install:

```bash
npm install
```

## Important Notes

### DO NOT Edit Bundle Files

The files in `vendor/frontend/output/` are auto-generated. Edit these instead:
- `vendor/frontend/css/frontend.css` - Tailwind import and custom CSS classes
- `custom.scss` - Non-Tailwind styles
- `tailwind.config.js` - Tailwind theme configuration
- `vendor/frontend/js/frontend.js` - JavaScript entry point
- HTML templates - Tailwind utility classes

### Always Commit Bundle Files

Commit production-ready bundles after `make frontend-prod`:
- No build step in Docker
- Faster deployments
- Consistent assets across environments

### Prefer Tailwind Utilities

Use Tailwind utility classes instead of writing custom CSS:

❌ **Avoid:**
```css
.my-button {
  padding: 8px 16px;
  background-color: blue;
  border-radius: 8px;
}
```

✅ **Prefer:**
```html
<button class="px-4 py-2 bg-blue-600 rounded-lg">
  Button
</button>
```

### Separation of Concerns

- **frontend.css**: Tailwind import (`@import "tailwindcss"`) + custom CSS classes
- **custom.scss**: Non-Tailwind styles, pure CSS/SCSS without any Tailwind features
- **frontend.js**: JavaScript entry point for all vendor imports and app code

## Troubleshooting

### CSS changes not appearing

1. Ensure watcher is running: `make frontend-dev`
2. Check for syntax errors in `frontend.css`
3. Clear browser cache (Ctrl+Shift+R / Cmd+Shift+R)

### Bundle files not updating

1. Stop watcher (Ctrl+C)
2. Delete bundle files:
   ```bash
   rm apps/web/static/vendor/frontend/output/bundle.css
   rm apps/web/static/vendor/frontend/output/bundle.js
   ```
3. Run `make frontend-prod`

### Tailwind classes not working

1. Verify template is in `tailwind.config.js` content array
2. Check class spelling
3. Rebuild with `make frontend-prod`
4. Check if using a custom class that needs to be added to config

### JavaScript not loading

1. Check browser console for errors
2. Verify `frontend.js` syntax is correct
3. Ensure imported libraries are installed via npm
4. Rebuild with `make frontend-prod`

## Resources

- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Tailwind Play](https://play.tailwindcss.com/) - Online playground
- [Tailwind UI](https://tailwindui.com/) - Official component library
- [esbuild Documentation](https://esbuild.github.io/)
