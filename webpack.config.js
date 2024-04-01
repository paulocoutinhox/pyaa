const path = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const TerserPlugin = require('terser-webpack-plugin');

module.exports = {
    entry: {
        'site-base': './assets/site-base.js',
        'site-tailwind': './assets/site-tailwind.js',
        'site': './assets/javascript/site.js',
    },
    output: {
        path: path.resolve(__dirname, './static'),
        filename: 'js/[name]-bundle.js',
        library: ["SiteJS", "[name]"],
    },
    resolve: {
        extensions: ['.js', '.jsx', '.ts', '.tsx'],
    },
    module: {
        rules: [
            {
                test: /\.(js|jsx|ts|tsx)$/,
                exclude: /node_modules/,
                loader: "babel-loader",
            },
            {
                test: /\.scss$/,
                use: [
                    MiniCssExtractPlugin.loader,
                    'css-loader',
                    'sass-loader',
                ],
            },
            {
                test: /\.css$/i,
                use: [
                    MiniCssExtractPlugin.loader,
                    'css-loader',
                    'postcss-loader'
                ],
            },
        ],
    },
    plugins: [
        new MiniCssExtractPlugin({
            'filename': 'css/[name].css',
        }),
    ],
    optimization: {
        minimizer: [new TerserPlugin({
            extractComments: false,  // disable generation of license.txt files
        })],
    },
};
