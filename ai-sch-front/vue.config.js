'use strict'
const path = require('path')

function resolve(dir) {
  return path.join(__dirname, dir)
}

// 设置端口号
const port = process.env.port || process.env.npm_config_port || 8080

// 所有配置项说明可在 https://cli.vuejs.org/config/ 查看
module.exports = {
  publicPath: '/',
  outputDir: 'dist',
  assetsDir: 'static',
  lintOnSave: false,
  productionSourceMap: false,
  devServer: {
    port: port,
    open: true,
    overlay: {
      warnings: false,
      errors: true
    },
    proxy: {
      // 设置代理
      [process.env.VUE_APP_BASE_API]: {
        target: `http://localhost:8000`,
        changeOrigin: true,
        pathRewrite: {
          ['^' + process.env.VUE_APP_BASE_API]: ''
        }
      }
    }
  },
  configureWebpack: {
    // 在webpack的名称字段中提供应用程序的标题
    name: '智能排课系统',
    resolve: {
      alias: {
        '@': resolve('src')
      }
    }
  }
} 
