# WebApp

You can place your static application in the `apps/web/static/app` directory. This setup allows you to serve the application from the `/app` URL path on your host. This is particularly useful for applications built with frameworks like Vue.js or React.

## Steps To Deploy A Static Application

1. **Build Your Application**: Ensure your Vue.js or React application is built and ready for deployment. Typically, this involves running a build command such as `npm run build` or `yarn build`.

2. **Copy Build Files**: Once your application is built, copy the output files (usually found in the `dist` or `build` directory) to the `apps/web/static/app` directory of your project.

3. **Access the Application**: After copying the files, your static application will be accessible at `http://your-host/app/`.

## Example

If you have a Vite application, follow these steps:

1. Build the application:
    ```bash
    npm run build
    ```

2. Copy the build output to the `apps/web/static/app` directory:
    ```bash
    rm -rf path/to/your/project/apps/web/static/app/
    cp -r dist/* path/to/your/project/apps/web/static/app/
    ```

3. Access your application at `http://your-host/app/`.

## Component Cheatsheet / Test Page

The project includes a comprehensive Bootstrap component cheatsheet page for testing and development purposes. This page displays all Bootstrap components with the custom design system applied, allowing you to visualize how components appear in both light and dark modes.

### Accessing the Cheatsheet

The cheatsheet is available at:

```
http://your-host/test/cheatsheet/
```

### Features

- **Complete Component Library**: Displays all Bootstrap components including:
  - Typography (headings, displays, text formatting)
  - Images and figures
  - Tables (striped, bordered, hover, colored rows)
  - Forms (inputs, selects, checkboxes, radios, validation states)
  - Components (accordion, alerts, badges, breadcrumbs, buttons, cards, carousel, dropdowns, list groups, modals, navs, navbar, pagination, popovers, progress, scrollspy, spinners, toasts, tooltips)
