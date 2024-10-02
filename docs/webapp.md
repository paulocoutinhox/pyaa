# WebApp

You can place your static application in the `static/app` directory. This setup allows you to serve the application from the `/app` URL path on your host. This is particularly useful for applications built with frameworks like Vue.js or React.

## Steps to Deploy a Static Application

1. **Build Your Application**: Ensure your Vue.js or React application is built and ready for deployment. Typically, this involves running a build command such as `npm run build` or `yarn build`.

2. **Copy Build Files**: Once your application is built, copy the output files (usually found in the `dist` or `build` directory) to the `static/app` directory of your project.

3. **Access the Application**: After copying the files, your static application will be accessible at `http://your-host/app/`.

## Example

If you have a Vue.js application, follow these steps:

1. Build the application:
    ```bash
    npm run build
    ```

2. Copy the build output to the `static/app` directory:
    ```bash
    rm -rf path/to/your/project/static/app/
    cp -r dist/* path/to/your/project/static/app/
    ```

3. Access your application at `http://your-host/app/`.

