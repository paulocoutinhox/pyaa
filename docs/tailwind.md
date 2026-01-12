# Tailwind CSS

This project uses **Tailwind CSS v4** for styling. The CSS build pipeline is managed by npm using the Tailwind CLI.

## Architecture

The CSS architecture follows this structure:

```
apps/web/static/css/
├── tailwind/
│   ├── tailwind.css    # Tailwind directives (input file)
│   └── bundle.css      # Final compiled CSS (output file, DO NOT edit manually)
├── main.scss           # SCSS entry point for custom styles
└── custom.scss         # Project-specific custom styles
```

### Key Files

- **tailwind/tailwind.css**: Input file with Tailwind directives (`@tailwind base`, `@tailwind components`, `@tailwind utilities`)
- **tailwind/bundle.css**: Final compiled Tailwind CSS (auto-generated, committed to repository)
- **main.scss**: SCSS entry point that imports custom styles
- **custom.scss**: Project-specific custom styles and overrides

## Configuration Files

### tailwind.config.js

Tailwind scans all HTML templates:

```javascript
export default {
  darkMode: 'class',
  content: ['./templates/**/*.html'],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

## Build Commands

The project provides two build modes:

### Development with Watch Mode

For active development with automatic rebuilding:

```bash
make tailwind-dev
```

or:

```bash
npm run css:dev
```

Watches for changes in HTML templates and CSS files, automatically recompiling Tailwind.

### Production Build (Minified)

For production deployment with minified CSS:

```bash
make tailwind-prod
```

or:

```bash
npm run css:prod
```

**Important**: Always use `make tailwind-prod` before committing CSS changes. The minified `bundle.css` should be committed to avoid rebuilding in Docker.

## Workflow

### Development Workflow

1. Start the CSS watcher:
   ```bash
   make tailwind-dev
   ```

2. Start the Django server:
   ```bash
   make run
   ```

3. Edit HTML templates or CSS files
4. Changes automatically compile to `apps/web/static/css/tailwind/bundle.css`

### Before Committing

Always generate the production version:

```bash
make tailwind-prod
git add apps/web/static/css/tailwind/bundle.css
git commit -m "update styles"
```

This ensures optimized CSS is available in production without requiring a build step in Docker.

## Using Tailwind

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

## Custom Styles

The `custom.scss` file is for project-specific customizations. While Tailwind utilities should be preferred, `custom.scss` is useful for:

### When to Use custom.scss

- Complex component styles that can't be expressed with utilities alone
- Reusable component patterns
- Custom animations and transitions
- Third-party library overrides

### Example

```scss
// custom.scss
.custom-card {
  @apply p-6 bg-white rounded-lg shadow-md;

  // custom property not available in Tailwind
  border-left: 4px solid #3b82f6;
}

.custom-animation {
  @apply transition-all duration-300;

  &:hover {
    transform: translateY(-2px);
  }
}
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
  "tailwindcss": "latest",
  "@tailwindcss/cli": "latest"
}
```

Install:

```bash
npm install
```

## Important Notes

### DO NOT Edit bundle.css

The `tailwind/bundle.css` file is auto-generated. Edit these instead:
- `tailwind/tailwind.css` - Tailwind directives
- `custom.scss` - Custom styles
- HTML templates - Tailwind utility classes

### Always Commit bundle.css

Commit production-ready `bundle.css` after `make tailwind-prod`:
- No build step in Docker
- Faster deployments
- Consistent CSS across environments

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

## Troubleshooting

### CSS changes not appearing

1. Ensure watcher is running: `make tailwind-dev`
2. Check for SCSS syntax errors
3. Clear browser cache (Ctrl+Shift+R / Cmd+Shift+R)

### Bundle.css not updating

1. Stop watcher (Ctrl+C)
2. Delete `apps/web/static/css/tailwind/bundle.css`
3. Run `make tailwind-prod`

### Tailwind classes not working

1. Verify template is in `tailwind.config.js` content array
2. Check class spelling
3. Rebuild with `make tailwind-prod`
4. Check if using a custom class that needs to be added to config

## Resources

- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Tailwind Play](https://play.tailwindcss.com/) - Online playground
- [Tailwind UI](https://tailwindui.com/) - Official component library
