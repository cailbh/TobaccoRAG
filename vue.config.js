const {defineConfig} = require('@vue/cli-service')
module.exports = defineConfig({
  //close eslint 防止报错
  lintOnSave: false,
  publicPath: "./",
  assetsDir: "static",
  outputDir: 'dist',
  transpileDependencies: [
    'docx-preview',
  ],
  devServer: {
      headers: { 'Access-Control-Allow-Origin': '*' },
      proxy: {
          '/api': {
              target: 'http://127.0.0.1:3000/',
              // target: 'http://localhost:3000/',
              changeOrigin: true,
              pathRewrite: {
                  '^/api': ''
              },
              onProxyReq: (proxyReq, req, res) => {
                if (req.method === 'POST' && req.body) {
                  const contentLength = Buffer.byteLength(req.body, 'utf-8');
    
                  proxyReq.setHeader('Content-Length', contentLength);
                }}
          }
      },

  },
  configureWebpack: (config) => {
      config.module.rules.push({
        test: /\.glsl$/,
        use: [
          {
            loader: "webpack-glsl-loader",
          },
        ],
      });
    },
})
