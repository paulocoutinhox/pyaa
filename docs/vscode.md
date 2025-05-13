# Visual Studio Code Configuration

This document provides information on how to configure Visual Studio Code (VSCode) for optimal development experience with PyAA.

## Recommended Settings

To ensure consistent code formatting and organization of imports, add the following configuration to your VSCode settings.

### User Settings Configuration

1. Open VSCode
2. Press `Cmd + Shift + P` (Mac) or `Ctrl + Shift + P` (Windows/Linux) to open the Command Palette
3. Type "Preferences: Open User Settings (JSON)" and select it
4. Add the following configuration:

```json
"[python]": {
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": "always"
    },
    "editor.defaultFormatter": "ms-python.black-formatter"
},
```

## Required Extensions

For the best development experience, install the following VSCode extensions:

1. **Python** (ms-python.python)
2. **Black Formatter** (ms-python.black-formatter)
3. **isort** (ms-python.isort)

## Keyboard Shortcuts

- `Cmd + S` (Mac) or `Ctrl + S` (Windows/Linux) - Save file and automatically format code
- `Cmd + P` (Mac) or `Ctrl + P` (Windows/Linux) - Quick file navigation

## Benefits

This configuration provides the following benefits:

- Automatic code formatting on save using Black formatter
- Automatic organization of imports on save
- Consistent code style across the project
